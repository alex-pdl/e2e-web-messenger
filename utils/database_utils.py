import sqlite3
import datetime

database = "users.db"
filler = "[(', )]"


def register(username, password_hash, public_key, private_key):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    # inserting username & password hash into the database
    info = [
        (username, password_hash, public_key, private_key)
    ]
    cursor.executemany(
        "INSERT INTO users (username,password,public_key,private_key) VALUES (?,?,?,?)", info)
    # committing changes & closing the connection
    connection.commit()
    connection.close()


def password_check(username, password):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT password FROM users WHERE username = (?)", (username,))
    # when the pass hash is fetched, it is in the form of a list and has many characters that aren't part of the hash
    hashed_pass = str(cursor.fetchall()).strip(filler)
    connection.commit()
    connection.close()

    if password == hashed_pass:
        return True
    else:
        return False


def retrieve_user_id(username):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = (?)", (username,))
    retrieved_id = str(cursor.fetchall()).strip(filler)
    connection.commit()
    connection.close()
    return retrieved_id


def retrieve_privatekey(username):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT private_key FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    encrypted_private_key = result[0]
    connection.close()
    return encrypted_private_key


def user_exists(username):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users")
    existing_users = cursor.fetchall()

    for i in existing_users:
        if username.casefold() == i[0].casefold():
            return i[0]

    return False


def create_chat_entry(user_1, user_2, aes_key_1, aes_key_2):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    values = [user_1, user_2, aes_key_1, aes_key_2]
    cursor.execute(
        "INSERT INTO chats (username_1, username_2, aes_key_1, aes_key_2) VALUES(?,?,?,?)", (values))
    connection.commit()
    connection.close()


def retrieve_chats(username):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT username_2 from chats WHERE username_1 = (?)", (username,))
    get_names = cursor.fetchall()

    cursor.execute(
        "SELECT username_1 from chats WHERE username_2 = (?)", (username,))
    get_names_2 = cursor.fetchall()

    chat_names = []
    for i in get_names_2:
        chat_names.append(str(i).strip(filler))
    for i in get_names:
        chat_names.append(str(i).strip(filler))
    return chat_names


def retrieve_chatid(username_1, username_2):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT chatid FROM chats WHERE (username_1 = '{username_1}' AND username_2 = '{username_2}') OR (username_1 = '{username_2}' AND username_2 = '{username_1}')")
    chat_id = str(cursor.fetchone()).strip(filler)
    connection.close()
    return chat_id


def create_message(chat_id, timestamp, sender, contents):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("INSERT INTO message (sender, chat_id, contents, timestamp) VALUES (?, ?, ?, ?)",
                   (sender, chat_id, contents, timestamp))

    connection.commit()
    connection.close()


def retrieve_messages(chat_id):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT timestamp, sender FROM message WHERE chat_id = ? ORDER BY timestamp", (chat_id,))
    message_info = cursor.fetchall()
    cursor.execute(
        f"SELECT contents FROM message WHERE chat_id = ? ORDER BY timestamp", (chat_id,))
    contents = cursor.fetchall()

    return message_info, contents


def retrieve_public_key(username):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT public_key FROM users WHERE username = (?)", (username,))
    public_key = str(cursor.fetchone()).strip(filler)
    connection.close()
    return public_key


def get_aes_key(chatid, username):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute(
        f"SELECT aes_key_1 FROM chats WHERE chatid = '{chatid}' AND username_1 = '{username}'")

    aes_key = str(cursor.fetchone()).strip(filler)

    if aes_key == 'None':
        cursor.execute(
            f"SELECT aes_key_2 FROM chats WHERE chatid = '{chatid}' AND username_2 = '{username}'")

        aes_key = str(cursor.fetchone()).strip(filler)

    connection.close()

    return aes_key


def create_database():
    # creates database with all tables if it doesn't already exist
    connection = sqlite3.connect(database)
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
                username_2 TEXT,
                aes_key_1 TEXT,
                aes_key_2 TEXT
            ) """
    cursor.execute(create_chats_table)
    create_message_table = """
        CREATE TABLE IF NOT EXISTS message (
        msg_id INTEGER PRIMARY KEY NOT NULL,
        sender TEXT,
        chat_id INTEGER,
        contents TEXT,
        timestamp DATETIME
    ) """
    cursor.execute(create_message_table)
    connection.commit()
    connection.close()
