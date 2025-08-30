import json
from flask import Flask, url_for, render_template, redirect, request, session, abort
from flask_socketio import SocketIO, emit

from utils.database_utils import (chats_retrieval, chat_creation,
                                  password_check, register, user_exists,
                                  retrieve_privatekey, retrieve_public_key,
                                  retrieve_chatid, determine_column,
                                  create_message, retrieve_messages,
                                  create_database, retrieve_user_id)

from crypto_algorithms import (generate_prime, key_gen, hash_password,
                               sym_encryption, sym_decryption,
                               rsa_encrypt, rsa_decrypt)

from utils.input_utils import (get_salt, get_iterations, get_key_size,
                               get_secret_key, special_char_checker,
                               ascii_checker, string_to_tuple)

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
    password_hash = hash_password(password, salt, iterations, prime_number)

    return password_check(username, password_hash)


def is_register_valid(username, password):
    if password == password.lower():
        raise ValueError(
            "Password must include at least one uppercase letter.")

    special_chars = special_char_checker(username)
    if len(special_chars) != 0:
        raise ValueError(
            f"Username cannot include special characters such as: {special_chars}")

    ascii_chars = ascii_checker(password)
    if len(ascii_chars) != 0:
        raise ValueError(
            f"Password contains invalid characters: {ascii_chars}")

    if user_exists(username) != False:
        raise ValueError("Username is already taken.")


def create_user(username, password):
    # Generates a public and private key for the user
    public_key, private_key = key_gen(keysize)
    # Encrypts the private key with the users password
    private_key = sym_encryption(str(private_key), password, 0, iterations)
    # Hashes the password
    password_hash = hash_password(password, salt, iterations, prime_number)

    register(username, password_hash, str(public_key), private_key)


def create_session(username, password):
    session['username'] = username
    session['usr_id'] = retrieve_user_id(username)

    encrypted_private_key = retrieve_privatekey(username)
    decrypted_private_key = sym_decryption(
        encrypted_private_key, password, 0, iterations)
    session['private_key'] = decrypted_private_key


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
socketio = SocketIO(app,  cors_allowed_origins="*")
# A standard homepage which redirects to the login page
# If a user already has session data stored in cookies,
# they will automatically be redirected to the chats page

# {username: sid}
sids = {}


@app.route('/')
def homepage():
    if 'usr_id' in session:
        return redirect(url_for('chats', name=session['username']))

    return redirect(url_for('login'))

# The login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usr_id' in session:  # Checks if user isn't already logged in
        return redirect(url_for('chats', name=session['username']))

    if request.method == "POST":
        # Gets data submitted
        username = request.form.get('username')
        password = request.form.get('password')

        if not is_login_valid(username, password):
            error = "You have not entered in the correct information. Please try again."
            return render_template("login.html", error=error)

        create_session(username, password)

        # If user entered in correct info store the username, user id and private key in cookies
        return redirect(url_for('chats', name=username))

    return render_template("login.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # Submitting info (loggin in) uses POST, whereas loading the page uses GET
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            is_register_valid(username, password)
        except ValueError as e:
            return render_template("registration.html", error=e)

        create_user(username, password)

        create_session(username, password)

        # Successfull registration message will be passed in place of error box
        return render_template("registration.html", error="Success")

    return render_template("registration.html")


@app.route('/chats/<name>', methods=['GET', 'POST'])
def chats(name):
    # Checks if user isn't already logged in
    if 'usr_id' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if name != username:
        abort(404)

    if request.form.get('logout') == 'clicked':
        session.clear()
        return redirect(url_for('login'))

    names = chats_retrieval(username)

    return render_template("chats.html", name=username, user_name=str(username), names=names)


@app.route('/message', methods=['GET', 'POST'])
def message():
    if 'usr_id' not in session:
        return redirect(url_for('login'))

    username = session['username']
    selected_name = request.args.get('selected_name')
    chatid = retrieve_chatid(username, selected_name)

    if chatid == 'None':
        return redirect(url_for('login'))

    if request.method == "POST":
        if request.form.get('return') == 'clicked':
            return redirect(url_for('chats', name=username))
        else:
            message = request.form.get('message')
            store_message(chatid, message, username, selected_name)

    private_key = string_to_tuple(session['private_key'])
    column = determine_column(username, chatid)
    msg_info, encrypted_msg_contents = retrieve_messages(chatid, column)

    msgs = decrypt_format_msgs(msg_info, encrypted_msg_contents, private_key)

    if len(msgs) == 0:
        msgs = ["It appears you don't have any chats with this person. Say hi!"]

    return render_template('message.html', selected_user=selected_name, messages=msgs)


@socketio.on('store_sid')
def store_sid(username):
    sids[username] = request.sid


@socketio.on('remove_sid')
def remove_sid(username):
    del sids[username]


@socketio.on('add_chat')
def add_chat(sender, receiver):
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
    socketio.run(app, debug=True)
