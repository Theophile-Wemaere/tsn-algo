import sqlite3
import hashlib 
from html import escape
from flask_argon2 import Argon2
import random
from datetime import datetime
import os
import functions.toolbox as tools

argon2 = None

def init(app):
    global argon2
    argon2 = Argon2(app)

def hash(input):
    """
    return hashed password with argon2
    """
    return argon2.generate_password_hash(input)

def generate_hashname(id_user):
    """
    generate a random hashed name to store files
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    exist = True
    while exist:
        hash = str(random.getrandbits(128))
        cursor.execute("SELECT * FROM users WHERE picture = ?",(hash,))
        row = cursor.fetchone()
        if row is None:
            db.close()
            return hash

# def get_id(email):
#     db = sqlite3.connect('database.db')
#     cursor = db.cursor()
#     cursor.execute("SELECT id_user FROM users WHERE email = ?",(email,))
#     row = cursor.fetchone()
#     db.close()
#     if row is not None:
#         return row[0]
#     else:
#         return False

#region users create & login

def check_existing(column, value):
    """
    check if a user already exist (email and username)
    return true if yes else false
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE ? = ?",(column,value))
    row = cursor.fetchone()
    db.close()
    if row is not None:
        return True
    return False

def create_user(username, email, password):
    """
    create a new user in the database
    return the newly created user id
    return bad_email or bad_username if already used
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    password = hash(password)
    email = escape(email)
    username = escape(username)

    if check_existing("email",email):
        return "bad_email"
    if check_existing("username",username):
        return "bad_username"

    # todo : handle already exisiting email
    data = (email, username, username, password)
    sql = """
    INSERT INTO users(email, username, displayname, password, role, created_at, last_update, gender, notification, localisation) 
    VALUES (?, ?, ?, ?, 'user', date(), datetime(), 'X', 'N', 'The Internet')"""
    cursor.execute(sql,data)
    db.commit()
    
    cursor.execute("""
        SELECT id_user
        FROM users
        WHERE email = ?
    """, (email,))

    id_user = cursor.fetchone()[0]   

    create_default_picture(id_user,cursor)
    db.commit()
    db.close()

    return id_user

def create_default_picture(id_user,cursor):
    """
    download a default profile picture 
    store the filename in the table
    """
    hash = generate_hashname(id_user)
    tools.get_profile_picture(hash)
    cursor.execute("UPDATE users SET picture = ? WHERE id_user = ?",(hash,id_user))

def check_login(input,password):
    """
    check login credentials to start a session
    return the id_user if creds match, else return False
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("""
        SELECT password,id_user
        FROM users
        WHERE email = ? OR username = ?
    """, (input,input))

    row = cursor.fetchone()
    print(row)
    db.close()

    if row is not None:
        db_password = row[0]
        id_user = row[1]
        if argon2.check_password_hash(db_password, password):
            return id_user
    return False
#endregion

#region sessions

def generate_token(id_user):
    """
    generate a random access token
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    exist = True
    while exist:
        hash = str(random.getrandbits(128))
        cursor.execute("SELECT * FROM sessions WHERE token = ?",(hash,))
        row = cursor.fetchone()
        if row is None:
            db.close()
            return hash

def start_session(id_user):
    """
    create an access token in the table sessions
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # delete any existing token for this user
    cursor.execute("DELETE FROM sessions WHERE id_user = ?",(id_user,))
    db.commit()

    token = generate_token(id_user)
    data = (id_user,token)
    cursor.execute("INSERT INTO sessions VALUES(?,?)",data)
    db.commit()
    db.close()
    return token

def check_session(id_user,token):
    """
    check if a session token is valid
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("SELECT * FROM sessions WHERE id_user = ? AND token = ?",(id_user,token))
    row = cursor.fetchone()
    db.close()
    print("Row:",row)
    if row is not None:
        print("session is valid")
        return True
    return False

def annihilate_session(id_user,token):
    """
    destroy an entry in the sessions table at logout
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # delete any existing token for this user
    cursor.execute("DELETE FROM sessions WHERE id_user = ?",(id_user,))
    db.commit()
    db.close()

#endregion

#region get users info
def get_user_data(id_user):
    """
    return user's data to display on the dashboard
    return a dico object
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    SELECT email, username, displayname, picture 
    FROM users WHERE id_user = ?
    """
    cursor.execute(sql,(id_user,))
    row = cursor.fetchone()
    user_data = {
        "email": row[0],
        "username": row[1],
        "displayname": row[2],
        "picture": row[3]
    }
    db.close()
    return user_data

def get_user_profile(id_user):
    """
    return the user profile info
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    SELECT username, displayname, gender, created_at, description, localisation, picture
    FROM users WHERE id_user = ?"""
    cursor.execute(sql,(id_user,))
    row = cursor.fetchone()
    data = {
        "username": row[0],
        "displayname": row[1],
        "gender": row[2],
        "creation": row[3],
        "description": row[4],
        "localisation": row[5],
        "picture": row[6]
    }

    cursor.execute("SELECT count(*) FROM relations WHERE followed = ?",(id_user,))
    data["followers"] = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM relations WHERE follower = ?",(id_user,))
    data["following"] = cursor.fetchone()[0]
    
    return data


#endregion