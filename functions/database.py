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
    cursor.execute(f"SELECT * FROM users WHERE {column} = ?",(value,))
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

    data = (email, username, username, password)
    sql = """
    INSERT INTO users(email, username, displayname, password, role, created_at, last_update, gender, notification, location) 
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
        if db_password == "default":
            # default users for debug and dev
            return id_user
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

    if not check_existing("id_user",id_user):
        return -1

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    SELECT email, username, displayname, picture, description 
    FROM users WHERE id_user = ?
    """
    cursor.execute(sql,(id_user,))
    row = cursor.fetchone()
    user_data = {
        "email": row[0],
        "username": row[1],
        "displayname": row[2],
        "picture": row[3],
        "description": row[4],
        "id": id_user
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
    SELECT username, displayname, gender, created_at, description, location, picture
    FROM users WHERE id_user = ?"""
    cursor.execute(sql,(id_user,))
    row = cursor.fetchone()
    data = {
        "username": row[0],
        "displayname": row[1],
        "gender": row[2],
        "creation": row[3],
        "description": row[4],
        "location": row[5],
        "picture": row[6]
    }

    cursor.execute("SELECT count(*) FROM relations WHERE followed = ?",(id_user,))
    data["followers"] = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM relations WHERE follower = ?",(id_user,))
    data["following"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT t.name
        FROM tags t
        INNER JOIN user_tags ut 
        ON ut.tag = t.id_tag
        WHERE ut.user = ?
        """,(id_user,))
    data["tags"] = [row[0] for row in cursor.fetchall()]

    return data

def get_user_followers(id_user):
    """"
    return followers of a user
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("SELECT DISTINCT follower FROM relations WHERE followed = ?",(id_user,))
    followers = [row[0] for row in cursor.fetchall()]
    users_info = []
    for user in followers:
        data = get_user_data(user)
        del data["email"]
        users_info.append(data)

    return users_info

def get_user_following(id_user):
    """"
    return follows of a user
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("SELECT DISTINCT followed FROM relations WHERE follower = ?",(id_user,))
    followers = [row[0] for row in cursor.fetchall()]
    users_info = []
    for user in followers:
        data = get_user_data(user)
        del data["email"]
        users_info.append(data)

    return users_info

#endregion

#region update user info

def update_profile(id_user,displayname,description,location,gender):
    """
    update a user profile
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    UPDATE users SET 
    displayname = ?,
    description = ?,
    location = ?,
    gender = ?,
    last_update = datetime()
    WHERE id_user = ?
    """
    data = (displayname,description,location,gender,id_user)
    cursor.execute(sql,data)
    db.commit()
    db.close()

def update_picture(id_user,hash):
    """
    update the picture hash for a user
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    UPDATE users SET
    picture = ?
    WHERE id_user = ?
    """
    cursor.execute(sql,(hash,id_user))
    db.commit()
    db.close()

#endregion

#region recommandations

def get_user_recommandations(id_user):
    """
    return a dictionnary of users with a profile interesting to the current user
    """
    # let John be the current user
    # how it works -> the users potentially interesting for John are thoses :
    #    - users who posted something liked by john
    #    - users friends with friends of john
    #       (friend is when the follow is in both way)
    #    - users followed by users that John follow
    #    - users with the same interests as John (tags)
    #    - users liking the same posts than John
    #    - users that follow john
    # to be modified with a scoring system depending on likes, dislike (pattern matching)

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # get user tags
    cursor.execute("SELECT tag FROM user_tags WHERE user = ?",(id_user,))
    user_tags = [row[0] for row in cursor.fetchall()]

    # get users who posted something liked by current user
    cursor.execute("""
    SELECT DISTINCT p.author
    FROM posts p
    INNER JOIN posts_interaction pi
    ON pi.post = p.id_post WHERE pi.user = ? AND pi.action = 'L'
    """,(id_user,))
    author_liked = [row[0] for row in cursor.fetchall()]

    # get friends of current user friends
    cursor.execute("""
    SELECT r1.follower 
    FROM relations r1 
    INNER JOIN relations r2 
    ON r1.follower = r2.followed WHERE r2.follower=?
    """, (id_user,))
    friends_of_friends = [row[0] for row in cursor.fetchall()]

    # get users followed by users that the current users follow
    cursor.execute("""
    SELECT followed FROM relations
    WHERE follower IN (SELECT followed FROM relations WHERE follower = ?)
    AND followed NOT IN (SELECT followed FROM relations WHERE follower = ?)
    """,(id_user,id_user))
    followed_by_followed = [row[0] for row in cursor.fetchall()]

    # get users with the same interets as current user (with tags matching)
    cursor.execute(f"""
    SELECT user FROM user_tags 
    WHERE tag IN ({",".join(["?"]*len(user_tags))})
    AND user != ?
    """,user_tags + [id_user])
    users_same_interets = [row[0] for row in cursor.fetchall()]

    # get users liking the same posts as current user
    cursor.execute("""
    SELECT DISTINCT pi.user FROM posts_interaction pi 
    INNER JOIN posts_interaction pi2 
    ON pi.post = pi2.post 
    WHERE pi.user != ? AND pi2.user = ? AND pi2.action = 'L'
    """,(id_user,id_user))
    user_liking_same_posts = [row[0] for row in cursor.fetchall()]

    # get users following the current users
    cursor.execute("""
    SELECT follower FROM relations WHERE followed = ? 
    """,(id_user,))
    followers = [row[0] for row in cursor.fetchall()]

    potential_users = set(author_liked + 
    friends_of_friends + 
    followed_by_followed +
    users_same_interets + 
    user_liking_same_posts +
    followers)

    # check if we are not already following the user
    users = []
    for user in potential_users:
        cursor.execute("SELECT * FROM relations WHERE followed = ? AND follower = ?",(user,id_user))
        if cursor.fetchone() is None:
            users.append(user)
    db.close()

    users_info = []
    for user in users:
        print("user",user)
        data = get_user_data(user)
        if data != -1:
            del data["email"]
            users_info.append(data)
    
    return users_info

def update_relation(id_user,id_target,action):
    """
    update a relation (follow, unfollow)
    """

    if not check_existing("id_user",id_target):
        return "target_not_found"
    if not check_existing("id_user",id_user):
        return "user_not_found"

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    if action == "follow":
        cursor.execute("SELECT * FROM relations WHERE followed = ? AND follower = ?",(id_target,id_user))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO relations(followed,follower) VALUES(?,?)",(id_target,id_user))
            db.commit()
    elif action == "unfollow":
        cursor.execute("SELECT * FROM relations WHERE followed = ? AND follower = ?",(id_target,id_user))
        if cursor.fetchone() is not None:
            cursor.execute("DELETE FROM relations WHERE followed = ? and follower = ?",(id_target,id_user))
            db.commit()
    db.close()
    return "success"

def get_tags(id_user=None):
    """
    return all available tags from the database
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if id_user is None:
        cursor.execute("SELECT * FROM tags")
    else:
        cursor.execute("""
        SELECT t.id_tag, t.name
        FROM tags t
        INNER JOIN user_tags ut 
        ON ut.tag = t.id_tag
        WHERE ut.user = ?
        """,(id_user,))
    data = {}
    data["tags"] = {}
    for row in cursor.fetchall():
        data["tags"][row[1]] = row[0]
    db.close()
    return data

def update_tags(id_user,tags):
    """
    set a user tags
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_tags WHERE user = ?",(id_user,))
    db.commit()
    for tag in tags:
        cursor.execute("SELECT * FROM tags WHERE id_tag = ?",(tag,))
        if cursor.fetchone() is not None:
            cursor.execute("INSERT INTO user_tags VALUES(?,?)",(id_user,tag))
            db.commit()
    db.close()

#endregion

