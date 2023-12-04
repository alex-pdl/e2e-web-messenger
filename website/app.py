from flask import Flask, url_for, render_template, redirect, request, flash, session
from db_interaction import user_db_interaction
from db_interaction import chat_creation, chats_retrieval

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
        password = request.form.get('password')
        user = user_db_interaction(username,password)
        if user_db_interaction.register(user) != False:
            return redirect(url_for('login'))
        else:
            error = "Sorry, this username is currently in use."
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

        #chats doesn't work when you are automatically logged in by cookies, this is because user is only established if you go through the login page
        #this is why chats crashes when you try and retrieve names without loggin in first
        names = chats_retrieval(session['username'])
        return render_template("chats.html", user_name = str(session['username']),names = names,error=error)
    except:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'a98er23iur98erw980293dsfa'
    app.run(debug=True)