from flask import render_template, session
from flask import Flask, request, jsonify
import flask
import functions.database as db
import os
from datetime import timedelta
from dotenv import load_dotenv

@app.route("/api/file/upload", methods=["POST"])
def upload_file():
    if "calendar" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["calendar"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = file.filename
        id_user = db.get_id(session.get("email"))
        hashname = db.generate_hashname(id_user)
        file.save(os.path.join("files", hashname))
        db.save_file(id_user, filename, hashname)
        return "success"

    return jsonify({"error": "Failed to upload file"}), 500


@app.route("/api/file/latest_update", methods=["GET"])
def get_last_update():
    email = session.get("email")
    date = db.get_last_update(email)
    return date

# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- GUI functions

