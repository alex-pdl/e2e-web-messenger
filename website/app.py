from flask import Flask, url_for, render_template, redirect, request, flash, session
from db_interaction import user_db_interaction

app = Flask(__name__)

@app.route('/')
def homepage():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('chats'))

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = user_db_interaction(username,password)
        #if user entered in correct info:
        if user_db_interaction.password_check(user) == True:
            session['username'] = username
            #session['usr_id'] = user.retrieve_user_id()
            print(user.retrieve_user_id())

            return redirect(url_for('chats'))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/registration', methods = ['GET','POST'])
def registration():
    #submitting info uses POST, whereas loading the page uses GET
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_db_interaction(username,password)
        if user_db_interaction.register(user) != False:
            return redirect(url_for('login'))
    return render_template("registration.html")

@app.route('/chats', methods = ['GET','POST'])
def chats():
    print(session['username'])
    #print(session['usr_id'])
    return render_template("chats.html")


if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'a98er23iur98erw9'
    app.run(debug=True)