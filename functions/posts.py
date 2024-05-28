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
    visibility = request.form["visibility"]
    new_tags = []
    for tag in tags.split(','):
      new_tags.append(tag.replace('tag-',''))
    id_post = db.save_post(session.get('id'),visibility,title,post,new_tags)
    return {"code":"success","post":id_post}
  else:
    return redirect("/login",302)

@post_api.route("/edit", methods=['POST'])
def edit_post():
  if check_session(session):
    title = request.form["title"]
    tags = request.form["tags"]
    post = request.form["post"]
    id_post = request.form["id_post"]
    visibility = request.form["visibility"]
    new_tags = []
    for tag in tags.split(','):
      new_tags.append(tag.replace('tag-',''))
    code = db.edit_post(session.get('id'),id_post,visibility,title,post,new_tags)
    return {"code":code,"post":id_post}
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
      return {"code":"post_not_found"}

    if not db.check_post_visibility(id_user,data["id_author"],data["visibility"]):
      return redirect("/home")

    data["code"] = "success"
    if id_user == data["id_author"]:
      data["is_logged"] = "yes"
    return data
  else:
    return redirect('/home',302)

@post_api.route("/feed",methods=['GET'])
def get_post_feed():

  feed_filter = request.args.get('f')
  offset = request.args.get('offset')
  if feed_filter is None or feed_filter not in ['new','best','forme']:
    feed_filter = "new"

  if not tools.is_int(offset):
    offset = 0
    
  id_user = None
  if check_session(session):
    id_user = session.get('id')

  data = None
  if feed_filter == "new":
    data = db.get_feed_new(id_user,offset)
  elif feed_filter == "best":
    data = db.get_feed_best(id_user,offset) # add filter in time (best week, best month, best year,...)
  elif feed_filter == "forme":
    data = db.get_feed_forme(id_user,offset)
  
  data["code"] = "success"
  return data

@post_api.route("/action",methods=["PATCH"])
def post_action():
  if check_session(session):
    post = request.args.get("id_post")
    action = parse.unquote(request.args.get("action"))
    print(post,action)
    if post is not None and action in ['L+','L-','D+','D-','S+','S-'] :
      res = db.update_post_interaction(session.get('id'),post,action)
      return res
    else:
      return "bad_action_or_post"
  else:
    # TODO : return to login
    return "not_loggedin"

@post_api.route("/delete",methods=["DELETE"])
def delete_post():
  if check_session(session):
    post = request.args.get("id_post")
    if post is not None:
      res = db.delete_post(session.get('id'),post)
      return res
    else:
      return "no_post_specified"
  else:
    return redirect('/login',302)

@post_api.route("/comment/add",methods=['POST'])
def create_comment():
  if check_session(session):
    id_post = request.form['post']
    content = request.form['content']
    db.create_comment(session.get('id'),id_post,content)
    return "success"
  else:
    return redirect("/login",302)

@post_api.route("/comment/get",methods=['GET'])
def get_comments():
  id_user = None
  if check_session(session):
    id_user = session.get('id')
  id_post = request.args.get('id_post')
  if id_post is not None:
    data = db.get_comments(id_post,id_user)
    data["code"] = "success"
    return data
  else:
    return redirect('/home',302)

@post_api.route("/comment/delete",methods=["DELETE"])
def delete_comment():
  if check_session(session):
    comment = request.args.get("id_comment")
    if comment is not None:
      res = db.delete_comment(session.get('id'),comment)
      return res
    else:
      return "no_comment_specified"
  else:
    return redirect('/login',302)

@post_api.route("/search",methods=['GET'])
def search_post():
  query = request.args.get('q')
  if query is None:
    return {"code":"no_query"}
  data = db.search_post(query)
  data["code"] = "success"
  return data