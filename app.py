import json
from flask import Flask, url_for, render_template, redirect, request, session, abort
from flask_socketio import SocketIO, emit

from utils.database_utils import (retrieve_chats, create_chat_entry,
                                  password_check, register, user_exists,
                                  retrieve_privatekey, retrieve_public_key,
                                  retrieve_chatid, create_message,
                                  retrieve_messages, create_database,
                                  retrieve_user_id, get_aes_key)

from crypto_algorithms import (generate_prime)

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


def is_valid_chat(user_1, user_2):
    # checks if user tried to chat with themselves
    if user_1 == user_2:
        raise ValueError("You can't start a chat with yourself.")

    # checks if user 2 exists
    if not user_exists(user_2):
        error = "This user doesn't seem to exist. Maybe you misspelt their username?"
        raise ValueError(error)

    if retrieve_chatid(user_1, user_2) != "None":
        # Checks if user already has chat with this person
        raise ValueError(
            "You already have a chat with this person, you can't create another one.")


def is_register_valid(username):
    if not is_valid_username(username):
        raise ValueError("Username does not meet specified requirements")

    if user_exists(username) != False:
        raise ValueError("Username is already taken")


def create_session(username):
    session['username'] = username
    session['usr_id'] = retrieve_user_id(username)


# Beginning of the website code
app = Flask(__name__)
socketio = SocketIO(app, manage_session=False, cors_allowed_origins="*")
# A standard homepage which redirects to the login page
# If a user already has session data stored in cookies,
# they will automatically be redirected to the chats page

# {username: sid}
sids = {}
# {session_token: username}
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
    return render_template('message.html')


@socketio.on('verify_session')
def verify_session(session_token):
    if type(session_token) != str:
        emit('unverified', to=request.sid)
        return

    if session_token not in tokens:
        emit('unverified', to=request.sid)
        return

    user = tokens[session_token]

    sids[user] = request.sid

    emit('verified', user, to=sids[user])


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
    tokens[token] = username

    emit('success', token)


@socketio.on('login')
def login_user(username, password):
    sid = request.sid

    if not is_login_valid(username, password) or not is_valid_username(username):
        emit('display_error', "Invalid details", to=sid)
        return

    token = secrets.token_urlsafe(24)
    tokens[token] = username

    data = {
        'sessionToken': token,
        'publicKey': retrieve_public_key(username),
        'privateKey': retrieve_privatekey(username)
    }

    emit('success', data, to=sid)


@socketio.on('display_chats')
def display_chats(sessionToken):
    if sessionToken not in tokens:
        emit('unverified', to=request.sid)
        return

    user = tokens[sessionToken]

    if user is None:
        return

    chats = retrieve_chats(user)

    for chat in chats:
        socketio.emit('add_chat_btn', chat, to=sids[user])


@socketio.on('remove_sid')
def remove_sid(username):
    if username in sids:
        del sids[username]


@socketio.on('is_valid_chat_creation_request')
def is_valid_chat_creation_request(session_token, receiver):
    if session_token not in tokens:
        emit('unverified', to=request.sid)
        return

    sender = tokens[session_token]

    if sender is None:
        emit('unverified', to=request.sid)
        return

    sender_sid = sids.get(sender)

    # User may have input a valid username but with the wrong case,
    # User_exists returns correct case of requested username, if it exists
    case_correct_username = user_exists(receiver)

    if case_correct_username == False:
        e = "This user doesn't seem to exist. "\
            "Maybe you misspelt their username?"
        socketio.emit('display_error', e, to=sender_sid)
        return

    try:
        is_valid_chat(case_correct_username, sender)
    except ValueError as error:
        if sender_sid is not None:
            socketio.emit('display_error', str(error), to=sender_sid)
        return

    data = {
        'sender': sender,
        'receiver': case_correct_username,
        'sender_public_key': retrieve_public_key(sender),
        'receiver_public_key': retrieve_public_key(case_correct_username)
    }

    emit('generate_chat', data, to=sender_sid)


@socketio.on('create_chat')
def create_chat(chatData):
    if chatData['creator_token'] not in tokens:
        emit('unverified', to=request.sid)
        return

    user1 = tokens[chatData['creator_token']]

    if user1 != chatData['user1']:
        return

    create_chat_entry(
        user1,
        chatData['user2'],
        chatData['user1AesKey'],
        chatData['user2AesKey']
    )

    emit('add_chat_btn', chatData['user2'], to=sids[user1])


@socketio.on('verify_chat')
def verify_chat(chatData, session_token):
    requester = chatData['requester']
    chatWith = chatData['chatWith']

    if type(session_token) != str:
        emit('unverified', to=request.sid)
        return

    if session_token not in tokens:
        emit('unverified', to=request.sid)
        return

    if tokens[session_token] != chatData['requester']:
        return

    if not is_valid_username(chatData['chatWith']):
        return

    chatid = retrieve_chatid(requester, chatWith)

    if chatid is None:
        return

    aes_key = get_aes_key(chatid, requester)

    msg_info, msg_contents = retrieve_messages(chatid)

    data = {
        'chatId': chatid,
        'aesKey': aes_key,
        'messages': (msg_info, msg_contents)
    }

    if requester in sids:
        emit('initialise_chat', data, to=sids.get(requester))


@socketio.on('send_message')
def send_message(session_token, message):
    if session_token not in tokens:
        return

    if not isinstance(message, dict):
        return

    msg_chatid = message.get('chatid')
    sender = message.get('sender')
    receiver = message.get('receiver')
    contents = message.get('contents')
    timestamp = message.get('date')

    chatid = retrieve_chatid(sender, receiver)

    if chatid is None or chatid != msg_chatid:
        return

    if sender != tokens.get(session_token):
        return

    create_message(chatid, timestamp, sender, contents)

    if receiver in sids:

        msgData = {
            'sender': sender,
            'date': timestamp,
            'contents': contents
        }

        print(msgData)

        emit('receive_msg', msgData, to=sids.get(receiver))


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
