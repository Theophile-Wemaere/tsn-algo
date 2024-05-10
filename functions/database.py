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
    return argon2.generate_password_hash(input)

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

def generate_hashname(id_user):
    """
    generate a random hashed name
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    exist = True
    while exist:
        hash = str(random.getrandbits(128))
        cursor.execute("SELECT * FROM profil_pictures WHERE id_image = ?",(hash,))
        row = cursor.fetchone()
        if row is None:
            db.close()
            return hash

def get_id(email):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT id_user FROM users WHERE email = ?",(email,))
    row = cursor.fetchone()
    db.close()
    if row is not None:
        return row[0]
    else:
        return False

def check_existing(column, value):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE ? = ?",(column,value))
    row = cursor.fetchone()
    db.close()
    if row is not None:
        return True

def create_user(username, email, password):
    """
    create a new user in the database by sanitazing it's value and creating a unique ID
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
    data = (email, username, password)
    sql = """INSERT INTO users(email, username, password) VALUES (?, ?, ?)"""
    cursor.execute(sql,data)
    db.commit()
    
    cursor.execute("""
        SELECT id_user
        FROM users
        WHERE email = ?
    """, (email,))

    id_user = cursor.fetchone()[0]   
    db.close()

    create_default_picture(id_user)

    return id_user

def create_default_picture(id_user):

    hash = generate_hashname(id_user)
    tools.get_profile_picture(hash)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO profil_pictures VALUES(?,?)",(hash,id_user))
    db.commit()
    db.close()

def check_login(input,password):
    """
    check login credentials
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
            print("password ok !")
            return id_user
        else:
            print("bad password")
    return False

def start_session(id_user):
    """
    generate an access token in the table sessions
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

def get_user_data(id_user):
    """
    return user's data to display on the dashboard
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    SELECT u.email, u.username, u.displayname, u.gender, u.created_at, u.description,
        p.id_image
    FROM users u 
    INNER JOIN profil_pictures p ON u.id_user = p.user
    WHERE u.id_user = ?"""
    cursor.execute(sql,(id_user,))
    row = cursor.fetchone()
    user_data = {
        "email": row[0],
        "username": row[1],
        "displayname": row[2],
        "gender": row[3],
        "created_at": row[4],
        "description": row[5],
        "picture": row[6]
    }
    db.close()
    return user_data

def save_file(id_user,filename,hashname):
    """
    save file data in the files table
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # delete file for this user if there is one
    cursor.execute("SELECT hash_name FROM files WHERE id_user = ?",(id_user,))
    row = cursor.fetchone()
    print(row)
    if row is not None:
        hash_name = row[0]
        os.remove(os.path.join("files",hash_name))

    # delete any existing files entry for this user
    cursor.execute("DELETE FROM files WHERE id_user = ?",(id_user,))
    db.commit()

    date = datetime.now().strftime("%d/%m/%y at %Hh%M")
    data = (id_user,hashname,filename,date)
    cursor.execute("INSERT INTO files VALUES(?,?,?,?)",data)
    db.commit()
    db.close()
