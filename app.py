from flask import render_template, session
from flask import Flask, request, jsonify, redirect
import flask
import functions.database as db
from functions.user import check_session
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.getenv("FLASK_SECRET")
app.permanent_session_lifetime = timedelta(weeks=4)
db.init(app)

if not os.path.exists("static/pictures"):
    os.mkdir("static/pictures/")

if not os.path.exists("database.db"):
    print("Not database found")
    os.system("scripts/init.sh")


from functions.user import user_api
app.register_blueprint(user_api, url_prefix='/api/user')
from functions.posts import post_api
app.register_blueprint(post_api, url_prefix='/api/post')
from functions.messages import message_api
app.register_blueprint(message_api, url_prefix='/api/messages')

@app.route("/home")
@app.route("/")
def home():
    onboarding = request.args.get('onboarding')
    if onboarding is not None and onboarding == "true":
        return render_template('home.html',onboarding=True)
    return render_template('home.html',onboarding=False)


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/signin")
def signin():
    return render_template('signin.html')

@app.route("/profile")
def show_profile():
    id_user = request.args.get("id_user")
    if id_user is None: # if no id is given, show user profile
        if check_session(session):
            return render_template('profile.html',action="load_profile",id_user=session.get('id'))
        else:
            return redirect('/login',code=301)
    else: # else show the wanted user profile
        return render_template('profile.html',action="load_profile",id_user=id_user)

@app.route("/followers")
def show_followers():
    id_user = request.args.get("id_user")
    if id_user is None:
        if check_session(session):
            return render_template('profile.html',action="load_followers",id_user=session.get('id'))
        else:
            return redirect('/login',code=301)
    else: 
        return render_template('profile.html',action="load_followers",id_user=id_user)

@app.route("/following")
def show_following():
    id_user = request.args.get("id_user")
    if id_user is None:
        if check_session(session):
            return render_template('profile.html',action="load_following",id_user=session.get('id'))
        else:
            return redirect('/login',code=301)
    else: 
        return render_template('profile.html',action="load_following",id_user=id_user)

@app.route("/post/new")
def create_post():
    if check_session(session):
        return render_template("post-editor.html",title="Create a post", button="Create post")
    else:
        return redirect("/login",302)

@app.route("/post/edit")
def edit_post():
    if check_session(session):
        post = request.args.get('id_post')
        if post is not None:
            if not db.check_post_owner(session.get('id'),post):
                return redirect('/post/view/'+post,302)
            return render_template("post-editor.html",
            title="Edit your post",button="Edit post", edit="yes",id_post=post)
        else:
            return redirect('/home',302)
    else:
        return redirect("/login",302)

@app.route("/post/view/<int:id_post>")
def view_post(id_post):
    if id_post is not None:
        return render_template("post-view.html",id_post=id_post)

@app.route("/messages")
def view_messages():
    if check_session(session):
        conv = request.args.get('conv')
        if conv is not None:
            return render_template("messages.html",conv=conv)
        else:
            return render_template("messages.html",conv="none")
    else:
        return redirect("/login",302)

@app.route("/search")
def search():
    search_range = request.args.get('range')
    search_query = request.args.get('q')
    return render_template("search.html",range=search_range,query=search_query)

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0",port=5000)
    except KeyboardInterrupt:
        print("\nCtrl + C pressed, exiting...")
        exit(1)