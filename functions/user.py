from flask import render_template, session
from flask import Flask, request, jsonify, redirect
from html import escape
import flask
import functions.database as db
import os
from datetime import timedelta
from dotenv import load_dotenv

from flask import Blueprint
import functions.toolbox as tools

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
    else:
        # check if user is a follower / user follow it
        if check_session(session):
            is_follower,is_followed = db.get_user_relation(id_user,session.get('id'))
            data["is_followed"] = is_followed
            data["is_follower"] = is_follower
            data["session_ok"] = "yes"

    return data

@user_api.route('/activity/<int:id_user>')
def get_user_activity(id_user):
    if id_user is 0:
        if check_session(session):
            id_user = session.get('id')
        else:
            return redirect("/login",302)
    activity_type = request.args.get('type')
    if activity_type in ["dislikes","saved"] and id_user != session.get('id'):
        return {"code":"not_visible"}
    data = db.get_user_activity(id_user,activity_type)
    if id_user == session.get('id'):
        data["is_logged"] = "yes"
    data["code"] = "success"
    return data

@user_api.route('/settings', methods=['GET'])
def api_user_settings():
    if check_session(session):
        return render_template("settings.html",email=db.get_email(session.get('id')))
    else:
        return "login"

@user_api.route('/settings/update', methods=['PATCH'])
def api_settings_update():
    if check_session(session):
        email = request.form["email"]
        cpassword = request.form["cpassword"]
        npassword = request.form["npassword"]
        res = db.update_settings(session.get('id'),email,cpassword,npassword)
        return res
    else:
        return "login"

@user_api.route('/editor', methods=['GET'])
def api_user_editor():
    if check_session(session):
        return render_template("profile-editor.html")
    else:
        return "login"

@user_api.route('/profile/update', methods=['PATCH'])
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

@user_api.route('/profile/picture', methods=['PATCH'])
def api_picture_update():
    if check_session(session):
        if request.files["picture"]:
            file = request.files["picture"]
            if file.filename == "":
                return {"code":"no_file"}
            elif tools.allowed_file(file.filename):
                hash = db.generate_hashname(session.get('id'))
                file.save(f"static/pictures/{hash}.png")
                db.update_picture(session.get('id'),hash)
                return {"code":"success","hash":hash}
        else:
            return {"code":"no_file"}
    else:
        return redirect("/login",302)

@user_api.route('/followers/<int:id_user>')
def get_user_followers(id_user):
    if id_user is 0:
        if check_session(session):
            id_user = session.get('id')
        else:
            return redirect("/login",302)
    data = db.get_user_followers(id_user)
    res = {"code":"success","data":data}
    if id_user == session.get('id'):
        res["is_logged"] = "yes"
    return res

@user_api.route('/following/<int:id_user>')
def get_user_following(id_user):
    if id_user is 0:
        if check_session(session):
            id_user = session.get('id')
        else:
            return redirect("/login",302)
    data = db.get_user_following(id_user)
    res = {"code":"success","data":data}
    if id_user == session.get('id'):
        res["is_logged"] = "yes"
    return res
#endregion

#region recommandations

@user_api.route('/recommandations',methods=['GET'])
def api_recommandations():
    if check_session(session):
        t = request.args.get('t')
        if t is None:
            t = "post"
        
        if t == "user":
            data = db.get_user_recommandations(session.get('id'))
            return {"code":"success","data":data}
        elif t == "post":
            data = db.get_post_recommandations()
            data["code"] = "success"
            return data
    else:
        return redirect('/login',302)

@user_api.route('/relation',methods=['PATCH'])
def api_relation():
    if check_session(session):
        id_target = request.args.get("id_user")
        action = request.args.get("action")
        if id_target is None or action is None:
            return "bad_parameters"
        res = db.update_relation(session.get('id'),id_target,action)
        return res
    else:
        return redirect('/login',302)

@user_api.route('/preferences', methods=['GET'])
def api_preferences():
    if check_session(session):
        return render_template("preferences.html")

@user_api.route('/tags',methods=['GET'])
def api_tags():
    if check_session(session):
        user = request.args.get("user")
        data = None
        print("user : ",user)
        if user is not None and user == "true":
            data = db.get_tags(session.get('id'))
        else:
            data = db.get_tags()
        data["code"] = "success"
        return data
    else:
        return redirect('/login',302)

@user_api.route('/tags/update',methods=['PATCH'])
def api_tags_update():
    if check_session(session):
        tags = request.form["tags"].replace("tag-","").split(',')
        db.update_tags(session.get('id'),tags)
        return "success"
    else:
        return redirect('/login',302)
#endregion

@user_api.route("/search",methods=['GET'])
def search_user():
  query = request.args.get('q')
  if query is None:
    return {"code":"no_query"}
  data = db.search_user(query)
  data["code"] = "success"
  return data