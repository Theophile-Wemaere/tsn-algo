from flask import render_template, session
from flask import Flask, request, jsonify, redirect
from urllib import parse
from html import escape
import flask
import functions.database as db
import os
from datetime import timedelta
from dotenv import load_dotenv

from flask import Blueprint
import functions.toolbox as tools
from functions.user import check_session

# prefix : '/api/post'
post_api = Blueprint('post_api', __name__)

@post_api.route("/create", methods=['POST'])
def create_post():
  if check_session(session):
    title = request.form["title"]
    tags = request.form["tags"]
    post = request.form["post"]
    new_tags = []
    for tag in tags.split(','):
      new_tags.append(tag.replace('tag-',''))
    id_post = db.save_post(session.get('id'),0,title,post,new_tags)
    return {"code":"success","post":id_post}
  else:
    return redirect("/login",302)

@post_api.route("/get/<int:id_post>", methods=['GET'])
def get_post_info(id_post):
  if id_post is not None:
    id_user = None

    if check_session(session):
      id_user = session.get('id')

    data = db.get_post_info(id_post,id_user)

    if data == -1:
      return {"code":"tag_not_found"}
    data["code"] = "success"
    return data
  else:
    return redirect('/home',302)

@post_api.route("/action",methods=["PATCH"])
def post_action():
  if check_session(session):
    post = request.args.get("id_post")
    action = parse.unquote(request.args.get("action"))
    print(post,action)
    if post is not None and action in ['L+','L-','D+','D-','S+','S-'] :
      res = db.update_post_interaction(session.get('id'),post,action)
      if res == -1:
        return "post_not_found"
      else:
        return "success"
    else:
      return "bad_action_or_post"
  else:
    # TODO : return to login
    return "not_loggedin"