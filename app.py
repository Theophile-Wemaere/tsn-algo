from flask import render_template, session
from flask import Flask, request, jsonify
import flask
import functions.database as db
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")
app.permanent_session_lifetime = timedelta(weeks=4)
db.init(app)

if not os.path.exists("database.db"):
    print("Not database found, exiting")
    exit(1)


print(db.hash("Password123!"))

from functions.user import user_api
app.register_blueprint(user_api, url_prefix='/api/user')

@app.route("/home")
@app.route("/")
def home():
    return render_template('home.html')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/signin")
def signin():
    return render_template('signin.html')

@app.route("/profile")
def show_profile():
    id_user = request.args.get("id_user")
    if id_user is None: # if no id is given, show user profile
        return render_template('profile.html',id_user=session.get('id'))
    else: # else show the wanted user profile
        return render_template('profile.html',id_user=id_user)

if __name__ == '__main__':
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nCtrl + C pressed, exiting...")
        exit(1)