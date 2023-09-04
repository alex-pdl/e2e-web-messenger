from flask import Flask, url_for, render_template, redirect, request, flash
from db_interaction import user_db_interaction

app = Flask(__name__)

@app.route('/')
def homepage():
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_db_interaction(username,password)
        if user_db_interaction.password_check(user) == True:
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
def messages():
    return render_template("chats.html")


if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'a98er23iur98erw9'
    app.run(debug=True)