import json
from flask import Flask, url_for, render_template, redirect, request, session, abort
from flask_socketio import SocketIO, emit

from utils.database_utils import (retrieve_chats, chat_creation,
                                  password_check, register, user_exists,
                                  retrieve_privatekey, retrieve_public_key,
                                  retrieve_chatid, determine_column,
                                  create_message, retrieve_messages,
                                  create_database, retrieve_user_id)

from crypto_algorithms import (generate_prime, key_gen, hash_password,
                               sym_encryption, sym_decryption,
                               rsa_encrypt, rsa_decrypt)

from utils.input_utils import (get_salt, get_iterations, get_key_size,
                               get_secret_key, ascii_checker,
                               string_to_tuple, is_valid_username)

from utils.crypto_utils import hash_pass

import secrets

# The program requires certain parameters to run, I have given the user
# the option to generate these paramters upon first startup


def write_settings():
    salt = get_salt()
    iterations = get_iterations()
    prime_number = generate_prime(5)
    key_size = get_key_size()
    secret_key = get_secret_key()

    print(
        f"Here is your configuration:\n"
        f"Salt: {salt}\n"
        f"Iterations: {iterations}\n"
        f"Prime Number: {prime_number}\n"
        f"Key Size: {key_size}\n"
        f"Secret Key: {secret_key}"
    )

    settings = {"salt": salt,
                "iterations": iterations,
                "primenumber": prime_number,
                "key_size": key_size,
                "secret_key": secret_key}

    # Writing user defined settings to JSON file
    with open("settings.json", "w") as json_file:
        json.dump(settings, json_file)


def is_login_valid(username, password):
    # Hashes password submitted
    password_hash = hash_pass(password)

    return password_check(username, password_hash)


def is_register_valid(username):
    if not is_valid_username(username):
        raise ValueError("Username does not meet specified requirements")

    if user_exists(username) != False:
        raise ValueError("Username is already taken")


def create_session(username):
    session['username'] = username
    session['usr_id'] = retrieve_user_id(username)


def store_message(chatid, msg_contents, sender_username, receiver_username):
    sender_public_key = string_to_tuple(retrieve_public_key(sender_username))
    receiver_public_key = string_to_tuple(
        retrieve_public_key(receiver_username))

    # Create two versions of the message, 1 encrypted using the senders info,
    # and the other using the recievers info
    sender_message = str(rsa_encrypt(msg_contents, sender_public_key))
    receiver_message = str(rsa_encrypt(msg_contents, receiver_public_key))

    # Determine which column (contents_1 or contents_2) the sender is a part of
    which_contents = determine_column(session["username"], chatid)

    if which_contents == "contents_1":
        create_message(sender_username, chatid,
                       sender_message, receiver_message)
    elif which_contents == "contents_2":
        create_message(sender_username, chatid,
                       receiver_message, sender_message)


def decrypt_format_msgs(msg_info, encrypted_message_contents, private_key):
    messages = []

    for i in range(len(msg_info)):
        # Get each individual sender and timestamp
        info = msg_info[i]
        # Get each message (encrypted)
        encrypted_contents = encrypted_message_contents[i][0]
        # Format the sender and timestamp & append to messages
        formatted_info = str(info).replace(
            "(", "").replace(")", "").replace("'", "")
        messages.append(str(formatted_info))
        # Format the message contents and decrypt
        # Then add to messages list
        formatted_decrypted_message = ": " + \
            rsa_decrypt(encrypted_contents, private_key)
        messages[i] += formatted_decrypted_message

    return messages


# Beginning of the website code
app = Flask(__name__)
socketio = SocketIO(app, manage_session=False, cors_allowed_origins="*")
# A standard homepage which redirects to the login page
# If a user already has session data stored in cookies,
# they will automatically be redirected to the chats page

# {username: sid}
sids = {}
tokens = {}


@app.route('/')
def homepage():
    if 'usr_id' in session:
        return redirect(url_for('chats', name=session['username']))

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template("registration.html")


@app.route('/chats', methods=['GET', 'POST'])
def chats():
    return render_template("chats.html")


@app.route('/messages', methods=['GET', 'POST'])
def message():
    chatting_with = request.args.get('chatting_with')

    print(chatting_with)
    return render_template('message.html')


@socketio.on('verify_session')
def verify_session(data):
    if data['username'] not in tokens:
        emit('unverified', to=request.sid)
        return

    if tokens[data['username']] != data['sessionToken']:
        emit('unverified', to=request.sid)
        return

    sids[data['username']] = request.sid

    emit('verified', to=sids[data['username']])


@socketio.on('register_user')
def register_user(username, hashed_password, public_key, private_key):
    sid = request.sid

    try:
        is_register_valid(username)
    except ValueError as error:
        emit('display_error', str(error), to=sid)
        return

    doubleHashedPwd = hash_pass(hashed_password)

    register(username, doubleHashedPwd, public_key, private_key)

    token = secrets.token_urlsafe(24)
    tokens[username] = token

    emit('success', token)


@socketio.on('login')
def login_user(username, password):
    sid = request.sid

    if not is_login_valid(username, password) or not is_valid_username(username):
        emit('display_error', "Invalid details", to=sid)
        return

    token = secrets.token_urlsafe(24)
    tokens[username] = token

    data = {
        'sessionToken': token,
        'publicKey': retrieve_public_key(username),
        'privateKey': retrieve_privatekey(username)
    }

    emit('success', data, to=sid)


@socketio.on('display_chats')
def display_chats(sessionToken):
    for username_token in tokens.items():
        username = username_token[0]
        token = username_token[1]

        if token == sessionToken:
            user = username
            break

    if user == None or user not in sids:
        return

    chats = retrieve_chats(username)

    for chat in chats:
        socketio.emit('add_chat_btn', chat, to=sids[user])


@socketio.on('remove_sid')
def remove_sid(username):
    del sids[username]


@socketio.on('add_chat')
def add_chat(idToken, receiver):
    if idToken not in tokens.values():
        emit('unverified', to=sender_sid)

    # Finds sender's username, based on their session token
    for username_token in tokens.items():
        username = username_token[0]
        token = username_token[1]

        if token == idToken:
            sender = username
            break

    sender_sid = sids.get(sender)

    try:
        normalised_reciever_username = user_exists(receiver)

        if normalised_reciever_username == False:
            raise ValueError(
                "This user doesn't seem to exist. Maybe you misspelt their username?")

        receiver_sid = sids.get(normalised_reciever_username)

        chat_creation(normalised_reciever_username, sender)
    except ValueError as error:
        if sender_sid is not None:
            socketio.emit('display_error', str(error), to=sender_sid)
        return

    if sender_sid is not None:
        socketio.emit('add_chat_btn', normalised_reciever_username,
                      to=sender_sid)

    if receiver_sid is not None:
        # New button for reciever
        socketio.emit('add_chat_btn', sender, to=receiver_sid)
        # Added chat msg for reciever
        socketio.emit('new_chat_msg', sender, to=receiver_sid)


if __name__ == "__main__":
    while True:
        try:
            # Retrieving settings from .json file
            with open('settings.json', 'r') as file:
                data = json.load(file)
            print("\nSuccessfully detected settings.\n")

            salt = data["salt"]
            iterations = data["iterations"]
            prime_number = data["primenumber"]
            keysize = data["key_size"]
            secret_key = data["secret_key"]
            break
        except (FileNotFoundError, NameError):  # If the settings.json file doesn't exist
            print("Settings.json not detected. \nGenerating Settings.\n")

            write_settings()

            print("\nSettings configuration completed. The server will now start.\n")

    create_database()  # Initialise database upon running the program

    # Use secret key specified in settings.json file
    app.config['SECRET_KEY'] = f'{secret_key}'
    # Ensures that cookies are only accessible through HTTP(S) requests and cannot be accessed by any JavaScript
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    app.config['SESSION_TYPE'] = 'filesystem'
    socketio.run(app, debug=True)
