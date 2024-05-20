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