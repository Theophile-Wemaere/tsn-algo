## 𝕐 - The social network to talk about electronics !

This is a simple Flask application to play with recommendations algorithms, like FoaF (Friend of a Friend) and others.
It features various features like post creation/edition, comments, messaging, follows, ...

It use Flask as a backend and API, sqlite3 for the database and plain HTML,CSS and JS for frontend

> [!WARNING]
> This codebase is **highly** vulnerable to XSS and maybe other type of injection / IDOR / broken authentification
> I do not recommand using it in production without first reviewing the security

#### How to deploy

There are 2 (easy) ways to deploy this application :

**1. Docker**

Simply install docker (https://docs.docker.com/get-docker/) and then type :
```shell
$ docker-compose up --build
```
This should install all components of the app and have it running [](http://localhost:5000/)

**2. Manually**

This can also be done manually :
```shell
$ python3 -m virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ bash scripts/init.sh
$ echo "FLASK_SECRET=<your_secret_key>" >> .env
$ python app.py
```
