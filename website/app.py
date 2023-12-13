from flask import Flask, url_for, render_template, redirect, request, flash, session
from db_interaction import user_db_interaction
from db_interaction import chat_creation, chats_retrieval,create_message,retrieve_chatid,retrieve_messages,special_char_checker

app = Flask(__name__)

@app.route('/')
def homepage():
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
            
            global user
            user = user_db_interaction(username,password)
            #if user entered in correct info:
            if user_db_interaction.password_check(user) == True:
                session['username'] = username
                session['usr_id'] = user_db_interaction.retrieve_user_id(user)
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
    #submitting info (loggin in) uses POST, whereas loading the page uses GET
    if request.method == "POST":
        username = request.form.get('username')
        #makes sure username doesn't have special characters
        if special_char_checker(username) == None:
            password = request.form.get('password')
            user = user_db_interaction(username,password)
            if user_db_interaction.register(user) != False:
                return redirect(url_for('login'))
            else:
                error = "Sorry, this username is currently in use."
            return render_template("registration.html",error=error)
        else:
            error = f"Sorry, you cannnot have special characters such as: '{ str(special_char_checker(username)) }'  in your username."
            return render_template("registration.html",error=error)
    return render_template("registration.html")

@app.route('/chats', methods = ['GET','POST'])
def chats():
    #try and except is used as, if a user tries to reach the chats without logging in first, flask will produce an error
    try:
        error = ""
        if request.form.get('logout') == 'clicked':
            session.clear()
            return redirect(url_for('login'))
        if request.method == "POST":
            user2 = request.form.get('user_chat_name')
            chat_creation(session['username'],user2)
            if chat_creation(session['username'],user2) == "Error_1":
                error = "You already have a chat with this person, you can't create another one."
            elif chat_creation(session['username'],user2) == "Error_2":
                error = "This user doesn't seem to exist. Maybe you misspelt their username?"
            elif chat_creation(session['username'],user2) == "Error_3":
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
            create_message(session['username'],retrieve_chatid(session['username'],selected_name),message)
    try:
        messages = retrieve_messages(retrieve_chatid(session['username'],selected_name))
        return render_template('message.html',selected_user = selected_name,messages = messages)
    except:
        return redirect(url_for('chats'))

if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'a98er23iur98erw980293dsfa'
    app.run(debug=True, host='192.168.1.184')