from flask import render_template, session
from flask import Flask, request, jsonify
from html import escape
import flask
import functions.database as db
import os
from datetime import timedelta
from dotenv import load_dotenv

from flask import Blueprint

# prefix : '/api/user'
user_api = Blueprint('user_api', __name__)

def check_session(session):
    token = session.get('token')
    email = session.get('email')
    if email is not None and token is not None:
        return db.check_session(email, token)
    else:
        return False
        
@user_api.route('/is_logged', methods=['GET'])
def api_is_logged():
    if check_session(session):
        return "session_valid"
    return "session_invalid"

@user_api.route('/login', methods=['POST'])
def api_login():
    email = escape(request.form["email"])
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


@user_api.route('/update', methods=['POST'])
def api_user_update():
    check_session(session)
    print("ok here")
    return "ok"


@user_api.route('/logout', methods=['GET'])
def api_logout():
    email = session.get('email')
    token = session.get('token')
    db.annihilate_session(email, token)
    session.pop('email', None)
    session.pop('token', None)
    session.clear()
    return flask.redirect('/login')


@user_api.route('/signin', methods=['POST'])
def api_signin():
    email = request.form["email"]
    body = request.form["body"]
    res = db.store_request(email, body)
    if res:
        return "success"
    else:
        return "bad_email"