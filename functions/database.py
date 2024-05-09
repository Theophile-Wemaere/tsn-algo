import sqlite3
import hashlib 
from html import escape
from flask_argon2 import Argon2
import random
from datetime import datetime
import os

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
    generate a random access token
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    exist = True
    while exist:
        hash = str(random.getrandbits(128))
        cursor.execute("SELECT * FROM files WHERE hash_name = ?",(hash,))
        row = cursor.fetchone()
        if row is None:
            db.close()
            return hash


def get_id(email):
    hash_object = hashlib.md5()
    hash_object.update(email.encode('utf-8'))
    return hash_object.hexdigest() 

def create_user(username, email, password):
    """
    create a new user in the database by sanitazing it's value and creating a unique ID
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    password = hash(password)
    email = escape(email)
    username = escape(username) 
    id_user = get_id(email)
    # todo : handle already exisiting email
    data = (id_user, email, username, password)
    sql = """INSERT INTO users VALUES (?, ?, ?, ?, '', '')"""
    cursor.execute(sql,data)
    db.commit()
    db.close()

def check_login(email,password):
    """
    check login credentials
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    id_user = get_id(email)

    cursor.execute("""
        SELECT password
        FROM users
        WHERE id = ?
    """, (id_user,))

    row = cursor.fetchone()
    db.close()

    if row is not None:
        db_password = row[0]
        if argon2.check_password_hash(db_password, password):
            return id_user
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

def check_session(email,token):
    """
    check if a session token is valid
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    id_user = get_id(email)

    cursor.execute("SELECT * FROM sessions WHERE id_user = ? AND token = ?",(id_user,token))
    row = cursor.fetchone()
    db.close()
    print("Row:",row)
    if row is not None:
        print("session is valid")
        return True
    return False

def annihilate_session(email,token):
    """
    destroy an entry in the sessions table at logout
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    id_user = get_id(email)

    # delete any existing token for this user
    cursor.execute("DELETE FROM sessions WHERE id_user = ?",(id_user,))
    db.commit()
    db.close()

def get_user_data(email):
    """
    return user's data to display on the dashboard
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    id_user = get_id(email)
    cursor.execute("SELECT email,username,t_user FROM users WHERE id = ?",(id_user,))
    row = cursor.fetchone()
    user_data = {
        "email": row[0],
        "username": row[1],
        "t_user": row[2]
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

def get_last_update(email):
    """
    get the last update time for a user calendar file
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    id_user = get_id(email)
    cursor.execute("SELECT last_edited FROM files WHERE id_user = ?",(id_user,))
    row = cursor.fetchone()
    if row is not None:
        return row[0]
    else:
        return "<no file found>"

def store_request(email,body):
    """
    store a signin request for later validation
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # check if email already used
    id_user = get_id(email)
    cursor.execute("SELECT * FROM users WHERE id = ?",(id_user,))
    row = cursor.fetchone()
    if row is not None:
        return False

    email = escape(email)
    body = escape(body)

    cursor.execute("INSERT INTO requests (email,body) VALUES(?,?)",(email,body))
    db.commit()
    db.close()
    return True
