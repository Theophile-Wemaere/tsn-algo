from flask import render_template, session
from flask import Flask, request, jsonify
import flask
import functions.database as db
import os
from datetime import timedelta
from dotenv import load_dotenv

app = Flask(__name__)

@app.route('/api/user/login', methods=['POST'])
def api_login():
    email = request.form["email"]
    password = request.form["password"]
    res = db.check_login(email, password)
    if res:
        token = db.start_session(res)
        session["token"] = token
        session["email"] = email
        session.permanent = False
        return "redirect_user"
    else:
        return "bad_cred"


@app.route('/api/user/update', methods=['POST'])
def api_user_update():
    print("ok here")
    return "ok"


@app.route('/api/user/logout', methods=['GET'])
def api_logout():
    email = session.get('email')
    token = session.get('token')
    db.annihilate_session(email, token)
    session.pop('email', None)
    session.pop('token', None)
    session.clear()
    return flask.redirect('/login')


@app.route('/api/user/signin', methods=['POST'])
def api_signin():
    email = request.form["email"]
    body = request.form["body"]
    res = db.store_request(email, body)
    if res:
        return "success"
    else:
        return "bad_email"