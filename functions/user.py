from flask import render_template, session
from flask import Flask, request, jsonify, redirect
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

#region user profile
@user_api.route('/info/<int:id_user>')
def get_user_profile(id_user):
    if id_user is 0:
        if check_session(session):
            id_user = session.get('id')
        else:
            return redirect("/login",302)
    data = db.get_user_profile(id_user)
    if id_user == session.get('id'):
        data["is_logged"] = "yes"
    return data

@user_api.route('/editor', methods=['GET'])
def api_user_editor():
    if check_session(session):
        return render_template("profile-editor.html")

@user_api.route('/profile/update', methods=['POST'])
def api_profile_update():
    if check_session(session):
        displayname = request.form["displayname"]
        description = request.form["description"]
        location = request.form["location"]
        gender = request.form["gender"]
        if len(gender) == 1:
            db.update_profile(session.get('id'),displayname,description,location,gender)
            return "success"
        else:
            return "bad_gender"
    else:
        return "login"
#endregion

#region authentication
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

@user_api.route('/logout', methods=['GET'])
def api_logout():
    email = session.get('email')
    token = session.get('token')
    db.annihilate_session(email, token)
    session.pop('email', None)
    session.pop('token', None)
    session.clear()
    return flask.redirect('/login')
#endregion