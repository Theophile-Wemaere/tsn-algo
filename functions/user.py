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
    id_user = session.get('id')
    if id_user is not None and token is not None:
        return db.check_session(id_user, token)
    else:
        return False
        
@user_api.route('/is_logged', methods=['GET'])
def api_is_logged():
    user_info = {}
    user_info["code"] = "session_invalid"
    if check_session(session):
        user_info = db.get_user_data(session.get('id'))
        user_info["code"] = "session_valid"
    return user_info

@user_api.route('/login', methods=['POST'])
def api_login():
    email = escape(request.form["email"])
    password = request.form["password"]
    res = db.check_login(email, password)
    if res:
        token = db.start_session(res)
        session["token"] = token
        session["id"] = res
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
    username = request.form["username"]
    password = request.form["password"]
    res = db.create_user(username, email, password)
    if not str(res).startswith("bad"):
        token = db.start_session(res)
        session["token"] = token
        session["id"] = res
        session.permanent = False
        return "redirect_user"
    return res