from flask import render_template, session
from flask import Flask, request, jsonify
import flask
import functions.database as db
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")
app.permanent_session_lifetime = timedelta(minutes=30)
db.init(app)

if not os.path.exists("database.db"):
    print("Not database found, exiting")
    exit(1)

import functions.user
functions.user.app = app

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

if __name__ == '__main__':
    try:
        routes.init()
        app.run()
    except KeyboardInterrupt:
        print("\nCtrl + C pressed, exiting...")
        exit(1)