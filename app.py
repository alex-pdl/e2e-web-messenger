from flask import Flask, url_for, render_template, redirect, request, flash, session
from db_interaction import *
from algorithms import *
import json
import sys

# Retrieving settings from .json file
with open('settings.json', 'r') as file:
    data = json.load(file)

salt = data["salt"]
iterations = data["iterations"]
prime_number = data["primenumber"]
keysize = data["keysize"]

if keysize < 256:
    sys.exit("Please keep key length above 256! If not, the program will crash if you enter a message above the key size!")

print("Please change the default salt and prime number values within settings.json if not done so already!")

app = Flask(__name__)

@app.route('/')
def homepage():
    create_database()
    if 'usr_id' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('chats'))

@app.route('/login', methods = ['GET','POST'])
def login():
    if 'usr_id' not in session:
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            hashed_pass = hash_password(password,salt,iterations,prime_number)
            global user
            user = user_db_interaction(username,hashed_pass)
            # If user entered in correct info:
            if user_db_interaction.password_check(user) == True:
                session['username'] = username
                session['usr_id'] = user_db_interaction.retrieve_user_id(user)
                session['private_key'] = sym_decryption(user_db_interaction.retrieve_privatekey(user),password,0,iterations)
                return redirect(url_for('chats'))
            else:
                error = "You have not entered in the correct information. Please try again."
                return render_template("login.html",error=error)
        else:
            return render_template("login.html")
    else:
        return redirect(url_for('chats'))

@app.route('/registration', methods = ['GET','POST'])
def registration():
    create_database()
    # Submitting info (loggin in) uses POST, whereas loading the page uses GET
    if request.method == "POST":
        username = request.form.get('username')
        # Makes sure username doesn't have special characters
        if len(special_char_checker(username)) == 0:
            password = request.form.get('password')
            public_key,private_key = key_gen(keysize)
            private_key = sym_encryption(str(private_key),password,0,iterations)
            hashed_pass = hash_password(request.form.get('password'),salt,iterations,prime_number)
            user = user_db_interaction(username,hashed_pass,str(public_key),private_key)
            # Makes sure password doesn't have any characters that cannot be represented as ASCII values
            if len(ascii_checker(password)) == 0:
                if user_db_interaction.register(user) != False:
                    return redirect(url_for('login'))
                else:
                    error = "Sorry, this username is currently in use."
                return render_template("registration.html",error=error)
            else:
                error = f"Sorry, you password cannot contain the following special characters: {ascii_checker(password)}"
                return render_template("registration.html",error=error)
        else:
            error = f"Sorry, you cannnot have special characters such as: '{ str(special_char_checker(username)) }'  in your username."
            return render_template("registration.html",error=error)
    return render_template("registration.html")

@app.route('/chats', methods = ['GET','POST'])
def chats():
    # Try and except is used as, if a user tries to reach the chats without logging in first, flask will produce an error
    try:
        error = ""
        if request.form.get('logout') == 'clicked':
            session.clear()
            return redirect(url_for('login'))
        if request.method == "POST":
            user2 = request.form.get('user_chat_name')
            result = chat_creation(session['username'],user2)
            if result == "Error_1":
                error = "You already have a chat with this person, you can't create another one."
            elif result == "Error_2":
                error = "This user doesn't seem to exist. Maybe you misspelt their username?"
            elif result == "Error_3":
                error = "You can't start a chat with yourself."

        names = chats_retrieval(session['username'])
        return render_template("chats.html", user_name = str(session['username']),names = names,error=error)
    except:
        return redirect(url_for('login'))

@app.route('/message',methods = ['GET', 'POST'])
def message():
    selected_name = request.args.get('selected_name')
    if request.method == "POST":
        if request.form.get('return') == 'clicked':
            return redirect(url_for('chats'))
        else:
            message = request.form.get('message')
            # Create two versions of the message, 1 encrypted using the senders info, and the other using the recievers info
            receivers_message = RSA_Encrypt(message,string_to_tuple(retrieve_public_key(selected_name)))
            senders_message = RSA_Encrypt(message,string_to_tuple(retrieve_public_key(session['username'])))
            # Determine which column (contents_1 or contents_2) the sender is a part of
            chatid = retrieve_chatid(session["username"],selected_name)
            which_contents = determine_column(session["username"],chatid)
            if which_contents == "contents_1":
                create_message(session['username'],retrieve_chatid(session['username'],selected_name),str(senders_message),str(receivers_message))
            elif which_contents == "contents_2":
                create_message(session['username'],retrieve_chatid(session['username'],selected_name),str(receivers_message),str(senders_message))
    try:
        try:
            chatid = retrieve_chatid(session["username"],selected_name)
            which_contents = determine_column(session["username"],chatid)
            msg_info, encrypted_message_contents = retrieve_messages(retrieve_chatid(session['username'],selected_name),which_contents)
            messages = []
            for index in range(len(msg_info)):
                # Get each individual sender and timestamp
                info = msg_info[index]
                # Get each message (encrypted)
                encrypted_contents = encrypted_message_contents[index][0]
                # Format the sender and timestamp & append to messages
                formatted_info = str(info).replace("(", "").replace(")", "").replace("'", "")
                messages.append(str(formatted_info))
                # Format the message contents and decrypt
                # Then add to messages list
                formatted_decrypted_message = ": " + RSA_Decrypt(encrypted_contents,string_to_tuple(session['private_key']))
                messages[index] += formatted_decrypted_message
            return render_template('message.html',selected_user = selected_name,messages = messages)
        except:
            error = ["It appears you don't have any messages with this person."]
            return render_template('message.html',selected_user = selected_name,messages = error)
    except:
        return redirect(url_for('chats'))

if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'a98er23iur98erw980293dsfa'
    app.run(debug=True)