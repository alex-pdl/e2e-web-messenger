import json
import sys
from flask import Flask, url_for, render_template, redirect, request, session
from db_interaction import *
from algorithms import *


# The program requires certain parameters to run, I have given the user the option to generate these paramters
# Upon first startup
def write_settings():
    salt = ""
    iterations = 0
    prime_number = None
    keysize = 0
    secret_key = ""

    key_sizes = [256,512,1024,2048,4096]
    
    try:
        #Get password salt from the user.
        print("The password salt must be larger than 12 characters and cannot include spaces.")
        while len(salt) < 12 or " " in salt:
            try:
                salt = input("Please enter a salt for password hashing: ")
                if len(salt) < 12:
                    raise ValueError("Salt must be at least 12 characters long.")
                elif " " in salt:
                    raise ValueError("You cannot include spaces in your salt")
            except ValueError as e:
                print(f"\nError: {e}")
        
        #Get amount of iterations from the user
        print("\nEnter number of iterations for the symmetric encryption and hashing to go through. \n" + 
            "Note: With increasing number of iterations, security increases at the cost of speed.")

        while iterations < 3 or iterations > 50:
            try:
                iterations = input("Enter number of iterations: ")
                try:
                    iterations = int(iterations)
                except:
                    raise ValueError("You have not entered in an integer.")
                if iterations < 3 or iterations > 50:
                    raise ValueError("Must be between 3 and 50.")
            except ValueError as e:
                print(f"\nError: {e}")
                iterations = 0 # Restart to original value
                continue  # Restart if exception occurs
        print("Prime numbers are used by the hashing algorithm to produce hashes.")
        while True: 
            prime_choice = input("Would you like the program to generate a prime number ? (if not, you have to pick one) \n(y/n):")
            if prime_choice == "y" or prime_choice == "n":
                break
        if prime_choice == "y":
            # The prime number variable was initially set to none
            # Generating a prime number between 3 and 50
            while prime_number is None:
                random_number = random.randint(3, 50)
                if is_prime(random_number):
                    prime_number = random_number
        elif prime_choice == "n":
            # Get prime number from the user
            while prime_number is None:
                try:
                    prime_number = input("Please enter a prime number between 3 and 40: ")
                    # Make sure it is an integer
                    try:
                        prime_number = int(prime_number)
                    except:
                        raise ValueError("Please enter an integer.")
                    # Check if between 3 and 40
                    if prime_number < 3 or prime_number > 40:
                        raise ValueError("This must be between 3 and 40.")
                    # Check if prime
                    elif not is_prime(prime_number): # The is_prime() function returns the boolean TRUE if input is prime
                        raise ValueError("The number you have entered is not prime.")
                except ValueError as e:
                    print(f"\nError: {e} \n")
                    prime_number = None
                    continue  # Restart if exception occurs

        while True:
            key_size = input(f"\nChoose a key size for private public key encryption: {key_sizes}.\nKey Sizes above 2048 can slow down the program tremendously. \n 512 or 1024 is recommended.\nKey size: ")
            try:
                key_size = int(key_size)
                if key_size not in key_sizes:
                    raise ValueError
                else:
                    break
            except ValueError:
                print("\nPlease input an integer that is within the list.\n")
                continue
        
        print("\nThe secret key is the encryption key of the cookies.\nIt must be larger than 12 characters and cannot include spaces.")
        while len(secret_key) < 12 or " " in secret_key:
            try:
                secret_key = input("Please enter a secret key: ")
                if len(secret_key) < 12:
                    raise ValueError("It must be at least 12 characters long.")
                elif " " in secret_key:
                    raise ValueError("You cannot include spaces.")
            except ValueError as e:
                print(e)

    finally:
        print(f"Here is your configuration:\nSalt: {salt} \nIterations: {iterations} \nPrime Number: {prime_number} \nKey Size: {keysize} \nSecret Key: {secret_key}")
        settings = {
        "salt": salt,
        "iterations": iterations,
        "primenumber": prime_number,
        "key_size": key_size,
        "secret_key": secret_key
        }

        # Writing user defined settings to JSON file
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file)

# Beginning of the website code
app = Flask(__name__)
# A standard homepage which redirects to the login page
# If a user already has session data stored in cookies, they will automatically be redirected to the chats page

@app.route('/')
def homepage():
    if 'usr_id' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('chats'))

# The login page
@app.route('/login', methods = ['GET','POST'])
def login():
    total_users, total_chats, total_messages = statistics() # Gather general usage stats
    if 'usr_id' not in session: # Checks if user isn't already logged in
        if request.method == "POST":
            # Gets data submitted
            username = request.form.get('username')
            password = request.form.get('password')
            # Hashes password submitted
            hashed_pass = hash_password(password,salt,iterations,prime_number)
            global user
            user = user_db_interaction(username,hashed_pass)
            # If user entered in correct info store the username, user id and private key in cookies
            if user_db_interaction.password_check(user) == True:
                session['username'] = username
                session['usr_id'] = user_db_interaction.retrieve_user_id(user)
                session['private_key'] = sym_decryption(user_db_interaction.retrieve_privatekey(user),password,0,iterations)
                return redirect(url_for('chats'))
            else:
                error = "You have not entered in the correct information. Please try again."
                return render_template("login.html",error=error,total_users=total_users,total_chats=total_chats,total_messages=total_messages)
        else:
            return render_template("login.html",total_users=total_users,total_chats=total_chats,total_messages=total_messages)
    else:
        return redirect(url_for('chats'))

@app.route('/registration', methods = ['GET','POST'])
def registration():
    # Submitting info (loggin in) uses POST, whereas loading the page uses GET
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # Checks if username has any uppercase letters
        if password != password.lower():
            # Makes sure username doesn't have special characters
            if len(special_char_checker(username)) == 0:
                # Generates a public and private key for the user
                public_key,private_key = key_gen(keysize)
                # Encrypts the private key with the users password
                private_key = sym_encryption(str(private_key),password,0,iterations)
                # Hashes the password
                hashed_pass = hash_password(request.form.get('password'),salt,iterations,prime_number)
                user = user_db_interaction(username,hashed_pass,str(public_key),private_key)
                # Makes sure password doesn't have any characters that cannot be represented as ASCII values
                if len(ascii_checker(password)) == 0:
                    # If the register method returns false that means that the username is in use already
                    if user_db_interaction.register(user) != False:
                        # Redirect to login page
                        return redirect(url_for('login'))
                    else:
                        # Stay on the registration page and display the below error
                        error = "Sorry, this username is currently in use."
                    return render_template("registration.html",error=error)
                else:
                    error = f"Sorry, you password cannot contain the following special characters: {ascii_checker(password)}"
                    return render_template("registration.html",error=error)
            else:
                error = f"Sorry, you cannot have special characters such as: '{special_char_checker(username)}' in your username."
                return render_template("registration.html",error=error)
        else:
            error = "Please include at least one uppercase letter within your password."
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
        # If the user tries to access chats page without logging in first
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
        if len(messages) == 0:
            messages = ["It appears you don't have any chats with this person. Say hi!"]
        return render_template('message.html',selected_user = selected_name,messages = messages)
    except:
        return redirect(url_for('chats'))

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
        except (FileNotFoundError, NameError): # If the settings.json file doesn't exist
            print("Settings.json not detected. \nGenerating Settings.\n")
            
            write_settings()
            
            print("\nSettings configuration completed. The server will now start.\n")
        continue
    
    create_database() # Initialise database upon running the program
    
    app.config['SECRET_KEY'] = f'{secret_key}' # Use secret key specified in settings.json file
    app.config['SESSION_COOKIE_HTTPONLY'] = True # Ensures that cookies are only accessible through HTTP(S) requests and cannot be accessed by any JavaScript
    app.run(debug=True)