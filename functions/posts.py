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

@post_api.route("/link-preview", methods=['POST'])
def preview_link():
  # Simulate fetching data (replace with actual link fetching logic)
  title = "Example Title"
  description = "Example Description"
  image_url = "https://via.placeholder.com/150"

  # Build HTML response (replace with your desired HTML structure)
  preview_html = f"""
  <h2>{title}</h2>
  <p>{description}</p>
  <img src="{image_url}" alt="{title}">
  """

  # Return JSON response with preview HTML
  return jsonify({'preview_html': preview_html})

if __name__ == '__main__':
  app.run(debug=True)