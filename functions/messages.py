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

# prefix : '/api/messages'
message_api = Blueprint('message_api', __name__)

@message_api.route("/get/all",methods=['GET'])
def get_conversations():
    if check_session(session):
        conv = db.get_conversations(session.get('id'))
        conv["code"] = "success"
        return conv
    else:
        return redirect("/login",302)

@message_api.route("/get",methods=['GET'])
def get_conversation():
    if check_session(session):
        contact = request.args.get("contact")
        if contact is not None:
            conv = db.get_conversation(session.get('id'),contact)
            conv["code"] = "success"
            return conv
        else:
            return {"code":"no_contact"}
    else:
        return redirect('/login',302)

@message_api.route("/send",methods=['POST'])
def send_message():
    if check_session(session):
        contact = request.form["contact"]
        message = request.form["message"]
        db.add_message(session.get('id'),contact,message)
        return "success"
    else:
        return redirect("/login",302)