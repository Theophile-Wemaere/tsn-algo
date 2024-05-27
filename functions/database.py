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
        cursor.execute("SELECT * FROM users WHERE picture = ?", (hash,))
        row = cursor.fetchone()
        if row is None:
            db.close()
            return hash

def get_email(id_user):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT email FROM users WHERE id_user = ?",(id_user,))
    row = cursor.fetchone()
    db.close()
    if row is not None:
        return row[0]
    else:
        return False

# region users create & login

def check_existing(column, value):
    """
    check if a user already exist (email and username)
    return true if yes else false
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE {column} = ?", (value,))
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

    if check_existing("email", email):
        return "bad_email"
    if check_existing("username", username):
        return "bad_username"

    data = (email, username, username, password)
    sql = """
    INSERT INTO users(email, username, displayname, password, role, created_at, last_update, gender, notification, location) 
    VALUES (?, ?, ?, ?, 'user', date(), datetime(), 'X', 'N', 'The Internet')"""
    cursor.execute(sql, data)
    db.commit()

    cursor.execute("""
        SELECT id_user
        FROM users
        WHERE email = ?
    """, (email,))

    id_user = cursor.fetchone()[0]

    create_default_picture(id_user, cursor)
    db.commit()
    db.close()

    return id_user


def create_default_picture(id_user, cursor):
    """
    download a default profile picture 
    store the filename in the table
    """
    hash = generate_hashname(id_user)
    tools.get_profile_picture(hash)
    cursor.execute(
        "UPDATE users SET picture = ? WHERE id_user = ?", (hash, id_user))


def check_login(input, password):
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
    """, (input, input))

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
# endregion

# region sessions

def generate_token(id_user):
    """
    generate a random access token
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    exist = True
    while exist:
        hash = str(random.getrandbits(128))
        cursor.execute("SELECT * FROM sessions WHERE token = ?", (hash,))
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
    cursor.execute("DELETE FROM sessions WHERE id_user = ?", (id_user,))
    db.commit()

    token = generate_token(id_user)
    data = (id_user, token)
    cursor.execute("INSERT INTO sessions VALUES(?,?)", data)
    db.commit()
    db.close()
    return token


def check_session(id_user, token):
    """
    check if a session token is valid
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM sessions WHERE id_user = ? AND token = ?", (id_user, token))
    row = cursor.fetchone()
    db.close()
    print("Row:", row)
    if row is not None:
        print("session is valid")
        return True
    return False


def annihilate_session(id_user, token):
    """
    destroy an entry in the sessions table at logout
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # delete any existing token for this user
    cursor.execute("DELETE FROM sessions WHERE id_user = ?", (id_user,))
    db.commit()
    db.close()

# endregion

# region get users info

def get_user_data(id_user):
    """
    return user's data to display on the dashboard
    return a dico object
    """

    if not check_existing("id_user", id_user):
        print(f"user with id {id_user} doesn't exist")
        return -1

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    sql = """
    SELECT email, username, displayname, picture, description 
    FROM users WHERE id_user = ?
    """
    cursor.execute(sql, (id_user,))
    row = cursor.fetchone()
    user_data = {
        "email": row[0],
        "username": row[1],
        "displayname": row[2],
        "picture": row[3],
        "description": row[4],
        "id": id_user,
        "notread": 0
    }

    cursor.execute("""
    SELECT count(isread) 
    FROM messages
    WHERE "to" = ? AND isread = 'N'
    """,(id_user,))
    user_data["notread"] = cursor.fetchone()[0]
    
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
    cursor.execute(sql, (id_user,))
    row = cursor.fetchone()
    data = {
        "username": row[0],
        "displayname": row[1],
        "gender": row[2],
        "creation": row[3],
        "description": row[4],
        "location": row[5],
        "picture": row[6],
        "relations": None
    }

    cursor.execute(
        "SELECT count(*) FROM relations WHERE followed = ?", (id_user,))
    data["followers"] = cursor.fetchone()[0]
    cursor.execute(
        "SELECT count(*) FROM relations WHERE follower = ?", (id_user,))
    data["following"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT t.name
        FROM tags t
        INNER JOIN user_tags ut 
        ON ut.tag = t.id_tag
        WHERE ut.user = ?
        """, (id_user,))
    data["tags"] = [row[0] for row in cursor.fetchall()]

    return data

def get_user_relation(id_user1,id_user2):
    """
    check the relation of the user1 toward the user2
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    is_follower,is_followed = False,False

    cursor.execute("""
    SELECT * FROM relations
    WHERE followed = ? AND follower = ?
    """,(id_user1,id_user2))
    if cursor.fetchone() is not None:
        is_followed = True

    cursor.execute("""
    SELECT * FROM relations
    WHERE follower = ? AND followed = ?
    """,(id_user1,id_user2))
    if cursor.fetchone() is not None:
        is_follower = True

    db.close()
    return is_follower,is_followed

def get_user_activity(id_self,id_user,activity_type):
    """
    get activity (posts, liked, disliked and saved posts) for a user
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    posts = []

    if activity_type == "posts":
        # posts
        cursor.execute("""
        SELECT id_post FROM posts
        WHERE author = ? ORDER BY created_at DESC""",(id_user,))
        posts = [row[0] for row in cursor.fetchall()]
    elif activity_type == "likes":
        # likes
        cursor.execute("""
        SELECT post FROM posts_interaction
        WHERE user = ? AND action = 'L'""",(id_user,))
        posts = tools.reverse_list([row[0] for row in cursor.fetchall()])
    elif activity_type ==  "dislikes":
        # dislikes
        cursor.execute("""
        SELECT post FROM posts_interaction
        WHERE user = ? AND action = 'D'""",(id_user,))
        posts = tools.reverse_list([row[0] for row in cursor.fetchall()])
    elif activity_type == "saved":
        # saved
        cursor.execute("""
        SELECT post FROM posts_interaction
        WHERE user = ? AND action = 'S'""",(id_user,))
        posts = tools.reverse_list([row[0] for row in cursor.fetchall()])

    data = {
        "posts":  []
    }
    for post in posts:
        post_info = get_post_info(post,id_user)
        if check_post_visibility(id_self,post_info["id_author"],post_info["visibility"]):
            data["posts"].append(post_info)


    return data
    


def get_user_followers(id_user):
    """"
    return followers of a user
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute(
        "SELECT DISTINCT follower FROM relations WHERE followed = ?", (id_user,))
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

    cursor.execute(
        "SELECT DISTINCT followed FROM relations WHERE follower = ?", (id_user,))
    followers = [row[0] for row in cursor.fetchall()]
    users_info = []
    for user in followers:
        data = get_user_data(user)
        del data["email"]
        users_info.append(data)

    return users_info

def search_user(query):
    """
    search for user based on username, displayname and description
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    data = {
        "data":[]
    }

    query = f"%{query}%"

    # search in titles and contents:
    cursor.execute("""
    SELECT id_user
    FROM users
    WHERE username LIKE ?
    OR displayname LIKE ?
    OR description LIKE ?
    """,(query,query,query))
    users = [row[0] for row in cursor.fetchall()]

    users = list(set(users))
    for user in users:
        user_info = get_user_data(user)
        del user_info["email"]
        data["data"].append(user_info)

    db.close()
    return data

# endregion

# region update user info

def delete_account(id_user, password):
    """
    delete a user profil
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("""
    SELECT password
    FROM users
    WHERE id_user = ?""", (id_user,))
    existing_password = cursor.fetchone()
    if existing_password is not None:
        existing_password = existing_password[0]
        if argon2.check_password_hash(existing_password,password) or existing_password == "default":
            pass
        else:
            db.close()
            return "bad_password"
    else:
        db.close()
        return "login"
    
    cursor.execute("""
    DELETE FROM users 
    WHERE id_user = ?""",(id_user,))
    cursor.execute("""
    DELETE FROM posts 
    WHERE author = ?""",(id_user,))
    cursor.execute("""
    DELETE FROM comments 
    WHERE author = ?""",(id_user,))
    cursor.execute("""
    DELETE FROM posts_interaction
    WHERE user = ?""",(id_user,))
    cursor.execute("""
    DELETE FROM relations 
    WHERE followed = ? OR follower = ?""",(id_user,id_user))
    cursor.execute("""
    DELETE FROM user_tags 
    WHERE user = ?""",(id_user,))
    cursor.execute("""
    DELETE FROM sessions 
    WHERE id_user = ?""",(id_user,))
    cursor.execute("""
    DELETE FROM messages
    WHERE 'from' = ? OR 'to' = ?""",(id_user,id_user))

    db.commit()
    db.close()
    return "success"

def update_settings(id_user, email, current_password, new_password):
    """
    update a user profile
    """

    print(id_user,email,current_password,new_password)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("""
    SELECT password
    FROM users
    WHERE id_user = ?""", (id_user,))
    existing_password = cursor.fetchone()
    if existing_password is not None:
        existing_password = existing_password[0]
        if argon2.check_password_hash(existing_password,current_password) or existing_password == "default":
            pass
        else:
            db.close()
            return "bad_password"
    else:
        db.close()
        return "login"
    
    cursor.execute("""
    UPDATE users SET 
    email = ?
    WHERE id_user = ?""",(email,id_user))

    if new_password != "":
        hashed_password = hash(new_password)
        cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE id_user = ?""",(hashed_password,id_user))

    db.commit()
    db.close()
    return "success"

def update_profile(id_user, displayname, description, location, gender):
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
    data = (displayname, description, location, gender, id_user)
    cursor.execute(sql, data)
    db.commit()
    db.close()

def update_picture(id_user, hash):
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
    cursor.execute(sql, (hash, id_user))
    db.commit()
    db.close()

# endregion

# region recommandations

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
    cursor.execute("SELECT tag FROM user_tags WHERE user = ?", (id_user,))
    user_tags = [row[0] for row in cursor.fetchall()]

    # get users who posted something liked by current user
    cursor.execute("""
    SELECT DISTINCT p.author
    FROM posts p
    INNER JOIN posts_interaction pi
    ON pi.post = p.id_post WHERE pi.user = ? AND pi.action = 'L'
    """, (id_user,))
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
    """, (id_user, id_user))
    followed_by_followed = [row[0] for row in cursor.fetchall()]

    # get users with the same interets as current user (with tags matching)
    cursor.execute(f"""
    SELECT user FROM user_tags 
    WHERE tag IN ({",".join(["?"]*len(user_tags))})
    AND user != ?
    """, user_tags + [id_user])
    users_same_interets = [row[0] for row in cursor.fetchall()]

    # get users liking the same posts as current user
    cursor.execute("""
    SELECT DISTINCT pi.user FROM posts_interaction pi 
    INNER JOIN posts_interaction pi2 
    ON pi.post = pi2.post 
    WHERE pi.user != ? AND pi2.user = ? AND pi2.action = 'L'
    """, (id_user, id_user))
    user_liking_same_posts = [row[0] for row in cursor.fetchall()]

    # get users following the current users
    cursor.execute("""
    SELECT follower FROM relations WHERE followed = ? 
    """, (id_user,))
    followers = [row[0] for row in cursor.fetchall()]

    potential_users = set(author_liked +
                          friends_of_friends +
                          followed_by_followed +
                          users_same_interets +
                          user_liking_same_posts +
                          followers)
    
    potential_users = [user for user in potential_users if user != id_user]

    # check if we are not already following the user
    users = []
    for user in potential_users:
        cursor.execute(
            "SELECT * FROM relations WHERE followed = ? AND follower = ?", (user, id_user))
        if cursor.fetchone() is None:
            users.append(user)
    db.close()

    users_info = []
    for user in users:
        data = get_user_data(user)
        if data != -1:
            del data["email"]
            users_info.append(data)

    return users_info

def get_post_recommandations():
    """
    return the top post of the current week
    """

    db = sqlite3.connect("database.db")
    cursor = db.cursor()

    cursor.execute("""
    SELECT p.id_post
    FROM posts p
    LEFT JOIN (
        SELECT post, COUNT(*) AS like_count
        FROM posts_interaction
        WHERE action = 'L'
        GROUP BY post
    ) pi ON p.id_post = pi.post
    WHERE p.created_at >= DATE('now', '-7 days')
    ORDER BY pi.like_count DESC, p.created_at DESC
    LIMIT 10""")
    posts = [row[0] for row in cursor.fetchall()]

    data = {
        "posts":[]
    }
    for post in posts:
        post_info = get_post_info(post)
        data["posts"].append(post_info)

    db.close()
    return data

def update_relation(id_user, id_target, action):
    """
    update a relation (follow, unfollow)
    """

    if not check_existing("id_user", id_target):
        return "target_not_found"
    if not check_existing("id_user", id_user):
        return "user_not_found"

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    if action == "follow":
        cursor.execute(
            "SELECT * FROM relations WHERE followed = ? AND follower = ?", (id_target, id_user))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO relations(followed,follower) VALUES(?,?)", (id_target, id_user))
            db.commit()
    elif action == "unfollow":
        cursor.execute(
            "SELECT * FROM relations WHERE followed = ? AND follower = ?", (id_target, id_user))
        if cursor.fetchone() is not None:
            cursor.execute(
                "DELETE FROM relations WHERE followed = ? and follower = ?", (id_target, id_user))
            db.commit()
    elif action == "block":
        cursor.execute("""
        DELETE FROM relations 
        WHERE followed = ? AND follower = ? 
        """,(id_user,id_target))
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
        """, (id_user,))
    data = {}
    data["tags"] = {}
    for row in cursor.fetchall():
        data["tags"][row[1]] = row[0]
    db.close()
    return data

def update_tags(id_user, tags):
    """
    set a user tags
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_tags WHERE user = ?", (id_user,))
    db.commit()
    for tag in tags:
        cursor.execute("SELECT * FROM tags WHERE id_tag = ?", (tag,))
        if cursor.fetchone() is not None:
            cursor.execute("INSERT INTO user_tags VALUES(?,?)", (id_user, tag))
            db.commit()
    db.close()

# endregion

# region posts

def save_post(id_user, visibility, title, content, tags):
    """
    create a new post in the database
    visibility : 0 is public, 1 is private
    return post id
    """

    title = escape(title)

    visibility = 1 if visibility == "private" else 0

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO posts(author,visibility,title,content,created_at)
    VALUES (?,?,?,?,datetime())""", (id_user, visibility, title, content))
    id_post = cursor.lastrowid
    db.commit()
    for tag in tags:
        cursor.execute("SELECT * FROM tags WHERE id_tag = ?", (tag,))
        if cursor.fetchone() is not None:
            cursor.execute("INSERT INTO post_tags VALUES(?,?)", (id_post, tag))
            db.commit()

    db.close()
    return id_post

def check_post_owner(id_user, id_post):
    """
    check if a user is the given post owner
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    author = cursor.execute(
        "SELECT author FROM posts WHERE id_post = ?", (id_post,)).fetchone()
    db.close()
    if author is not None:
        if author[0] != id_user:
            return False
        else:
            print("User is owner")
            return True
    return False

def edit_post(id_user, id_post, visibility,title, content, tags):
    """
    edit post in database
    """

    title = escape(title)

    visibility = 1 if visibility == "private" else 0

    # check if user is owner
    if not check_post_owner(id_user, id_post):
        return "not_post_owner"

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("""
    UPDATE posts 
    SET title = ?, content = ?, visibility = ?
    WHERE id_post = ?""", (title, content, visibility, id_post))
    db.commit()

    cursor.execute("DELETE FROM post_tags WHERE post = ?",(id_post,))
    db.commit()
    for tag in tags:
        cursor.execute("SELECT * FROM tags WHERE id_tag = ?", (tag,))
        if cursor.fetchone() is not None:
            cursor.execute("INSERT INTO post_tags VALUES(?,?)", (id_post, tag))
            db.commit()

    db.close()
    return "success"

def get_post_info(id_post, id_user=None):
    """
    return the post data as a dict
    """

    data = {}

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("""
    SELECT p.title, p.content, p.author, u.displayname, u.picture ,p.created_at, p.visibility
    FROM posts p
    INNER JOIN users u
    ON u.id_user = p.author
    WHERE p.id_post = ?""", (id_post,))

    row = cursor.fetchone()
    if row is not None:
        data = {
            "id_post": id_post,
            "title": row[0],
            "content": row[1],
            "id_author": row[2],
            "author": row[3],
            "author_picture": row[4],
            "created_at": row[5],
            "visibility": row[6],
            "is_liked": False,
            "is_disliked": False,
            "is_saved": False
        }

        like = cursor.execute("""
        SELECT count(*) FROM posts_interaction 
        WHERE action = 'L' AND post = ?""", (id_post,)).fetchone()[0]
        data["like"] = 0 if like is None else like

        dislike = cursor.execute("""
        SELECT count(*) FROM posts_interaction 
        WHERE action = 'D' AND post = ?""", (id_post,)).fetchone()[0]
        data["dislike"] = 0 if dislike is None else dislike

        saved = cursor.execute("""
        SELECT count(*) FROM posts_interaction 
        WHERE action = 'S' AND post = ?""", (id_post,)).fetchone()[0]
        data["saved"] = 0 if saved is None else saved

        cursor.execute("""
        SELECT t.name, t.id_tag FROM tags t
        INNER JOIN post_tags pt
        ON pt.tag = t.id_tag
        WHERE pt.post = ?""", (id_post,))
        tags, id_tags = [], []
        for tag,id_tag in cursor.fetchall():
            tags.append(tag)
            id_tags.append(id_tag)
        data["tags"] = tags
        data["id_tags"] = id_tags
    else:
        data = -1

    if id_user is not None:
        is_liked = cursor.execute("""
        SELECT count(*) FROM posts_interaction
        WHERE action = 'L' AND post = ? AND user = ?""", (id_post, id_user)).fetchone()[0]
        data["is_liked"] = True if is_liked > 0 else False

        is_disliked = cursor.execute("""
        SELECT count(*) FROM posts_interaction
        WHERE action = 'D' AND post = ? AND user = ?""", (id_post, id_user)).fetchone()[0]
        data["is_disliked"] = True if is_disliked > 0 else False

        is_saved = cursor.execute("""
        SELECT count(*) FROM posts_interaction
        WHERE action = 'S' AND post = ? AND user = ?""", (id_post, id_user)).fetchone()[0]
        data["is_saved"] = True if is_saved > 0 else False

    db.close()
    return data

def search_post(query):
    """
    search for post based on title, content and comments
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    data = {
        "data":[]
    }

    query = f"%{query}%"

    # search in titles and contents:
    cursor.execute("""
    SELECT id_post
    FROM posts
    WHERE title LIKE ?
    OR content LIKE ?
    """,(query,query))
    posts = [row[0] for row in cursor.fetchall()]

    # search in comments
    cursor.execute("""
    SELECT DISTINCT(parent)
    FROM comments
    WHERE content LIKE ?
    """,(query,))
    posts = posts + [row[0] for row in cursor.fetchall()]

    posts = list(set(posts))
    for post in posts:
        post_info = get_post_info(post)
        data["data"].append(post_info)

    db.close()
    return data

def update_post_interaction(id_user, id_post, action):
    """
    update interaction from a user for a post
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id_post = ?", (id_post,))
    if cursor.fetchone() is None:  # post doesn't exist
        return "post_not_found"

    action_type = action[0]  # get L (like), D(dislike) or S(saved)
    action = action[1]  # get + or -
    cursor.execute(""" 
    SELECT * FROM posts_interaction
    WHERE post = ? AND action = ? AND user = ?""", (id_post, action_type, id_user))
    if cursor.fetchone() is not None:
        if action == "+":
            return  # cannot add to something already added
        elif action == "-":
            cursor.execute("""
            DELETE FROM posts_interaction 
            WHERE post = ? AND action = ? AND user = ?""", (id_post, action_type, id_user))
            db.commit()
    else:
        if action == "-":
            return  # cannot remove something not existing
        elif action == "+":
            cursor.execute("""
            INSERT INTO posts_interaction VALUES(?,?,?)""", (id_post, id_user, action_type))
            db.commit()

    db.close()
    return "success"

def delete_post(id_user, id_post):
    """
    delete a post from the database
    """

    if not check_post_owner(id_user, id_post):
        return "not_post_owner"

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM posts WHERE id_post = ?", (id_post,))
    cursor.execute("DELETE FROM posts_interaction WHERE post = ?", (id_post,))
    cursor.execute("DELETE FROM post_tags WHERE post = ?", (id_post,))
    cursor.execute("DELETE FROM comments WHERE parent = ?", (id_post,))
    db.commit()
    db.close()
    return "success"

def check_post_visibility(id_user,author,visibility):
    """
    check if a post can be show to a user depending of the visibility
    """

    print(id_user,author,visibility)

    if id_user == author:
        return True

    if id_user is None:
        print("Id user is none")
        if visibility == 1:
            return False
        else:
            return True

    if visibility == 1 :
        # post is private
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute("""
        SELECT * 
        FROM relations 
        WHERE followed = ? AND follower = ?""",(author,id_user))
        res = cursor.fetchone()
        db.close()
        if res is not None:
            # follow is true
            return True
        else:
            return False
    else:
        return True

def sort_post_by_tag(id_user, posts):
    """
    sort given posts by scoring them in relation with the user tags
    for exemple, a post with 3 common tags will have a better score than a score with 1 common tag 
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute("SELECT tag FROM user_tags WHERE user = ?", (id_user,))
    user_tags = [row[0] for row in cursor.fetchall()]

    posts_w_tags = {}
    for post in posts:
        cursor.execute("SELECT tag FROM post_tags WHERE post = ?", (post,))
        tags = [row[0] for row in cursor.fetchall()]
        posts_w_tags[post] = {}
        posts_w_tags[post]["tags"] = tags

    to_sort = []
    for post in posts_w_tags:
        score = 0
        for tag in posts_w_tags[post]["tags"]:
            if tag in user_tags:
                score += 1
        to_sort.append((score, post))

    sorted_posts = tools.merge_sort_recursive(to_sort)
    # set from highest score to lowest
    sorted_posts = tools.reverse_list(sorted_posts)
    return [post[1] for post in sorted_posts]

def get_feed_new(id_user=None, offset=0):
    """
    generate a feed of post sorted by time
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # first get post in relation with user preferences
    posts = []
    if id_user is not None:
        if not check_existing("id_user", id_user):
            return "unknow_id"

        cursor.execute("""
        SELECT p.id_post
        FROM posts p
        INNER JOIN relations r ON r.followed = p.author
        WHERE r.follower = ?
        ORDER BY p.created_at DESC LIMIT ?,10""", (id_user, offset))

        rows = cursor.fetchall()
        if rows is not None:
            posts = [post[0] for post in rows]
    
    if len(posts) == 0:
        cursor.execute("""
        SELECT id_post
        FROM posts
        ORDER BY created_at DESC
        LIMIT ?,10""",(offset,))
        posts = [row[0] for row in cursor.fetchall()]

    data = {
        "posts" : []
    }
    for post in posts:
        post_info = get_post_info(post,id_user)
        if check_post_visibility(id_user,post_info["id_author"],post_info["visibility"]):
            data["posts"].append(post_info)

    db.close()
    return data

def get_feed_best(id_user=None, offset=0):
    """
    generate a feed of post sorted by like count
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    posts = []

    cursor.execute(f"""
    SELECT p.id_post, 
    COUNT(CASE WHEN pi.action = 'L' THEN 1 END) AS like_count
    FROM posts p
    LEFT JOIN posts_interaction pi 
    ON p.id_post = pi.post
    GROUP BY p.id_post 
    ORDER BY like_count DESC
    LIMIT ?,10""", offset)
    rows = cursor.fetchall()
    if rows is not None:
        posts = [post[0] for post in rows]

    data = {
        "posts" : []
    }
    for post in posts:
        post_info = get_post_info(post,id_user)
        if check_post_visibility(id_user,post_info["author"],post_info["visibility"]):
            data["posts"].append(post_info)

    db.close()
    return data

def get_feed_forme(id_user=None, offset=0):
    """
    generate a feed of post sorted by time
    if a user id is supplied, the post will be in relation with the user tags
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    posts = []
    if id_user is not None:
        if not check_existing("id_user", id_user):
            return "unknow_id"
        cursor.execute("SELECT tag FROM user_tags WHERE user = ?", (id_user,))
        user_tags = [row[0] for row in cursor.fetchall()]

        cursor.execute(f"""
        WITH tagged_posts AS (
            SELECT p.id_post
            FROM posts p
            INNER JOIN post_tags pt ON pt.post = p.id_post
            WHERE pt.tag IN ({",".join(["?"]*len(user_tags))})
        ),
        followed_posts AS (
            SELECT p.id_post
            FROM posts p
            INNER JOIN relations r ON r.followed = p.author
            WHERE r.follower = ?
        )
        SELECT id_post
        FROM (
            SELECT id_post FROM tagged_posts
            UNION
            SELECT id_post FROM followed_posts
        ) AS combined_posts
        ORDER BY (
            SELECT created_at
            FROM posts
            WHERE id_post = combined_posts.id_post
        ) DESC
        LIMIT ?, 10
        """, user_tags + [id_user, offset])

        rows = cursor.fetchall()
        if rows is not None:
            posts = [post[0] for post in rows]
        print("before:",posts)
        # sort posts by scoring post tags with user tags
        posts = sort_post_by_tag(id_user, posts)
        print("after:",posts)
    
    if len(posts) == 0:
        cursor.execute("""
        SELECT id_post
        FROM posts
        ORDER BY created_at DESC
        LIMIT ?,10""",(offset,))
        posts = [row[0] for row in cursor.fetchall()]

    data = {
        "posts" : []
    }
    for post in posts:
        post_info = get_post_info(post,id_user)
        if check_post_visibility(id_user,post_info["author"],post_info["visibility"]):
            data["posts"].append(post_info)

    db.close()
    return data

# endregion

#region comments

def create_comment(id_user,id_post,content):
    """
    add a comment to a post in a database
    """

    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO comments(parent,author,content,created_at)
    VALUES(?,?,?,datetime())""",(id_post,id_user,content))
    db.commit()
    db.close()

def check_comment_owner(id_user, id_comment):
    """
    check if a user is the given comment owner
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    author = cursor.execute(
        "SELECT author FROM comments WHERE id_comment = ?", (id_comment,)).fetchone()
    db.close()
    if author is not None:
        if author[0] != id_user:
            return False
        else:
            print("User is owner")
            return True
    return False

def get_comments(id_post,id_user):
    """
    get all comments for a post
    """

    db = sqlite3.connect("database.db")
    cursor = db.cursor()

    cursor.execute("""
    SELECT id_comment,author,content,created_at
    FROM comments
    WHERE parent = ?
    ORDER BY created_at""",(id_post,))
    rows = cursor.fetchall()
    data = {
        "comments": []
    }
    if rows is not None:
        for row in rows:
            comment_info = {
                "id_post": id_post,
                "id_comment": row[0],
                "id_author": row[1],
                "content": row[2],
                "created_at": row[3],
                "is_author": False
            }

            author_info = get_user_data(comment_info["id_author"])
            comment_info["author"] = author_info["displayname"]
            comment_info["author_picture"] = author_info["picture"]

            if id_user is not None and id_user == comment_info['id_author']:
                comment_info["is_author"] = "yes"

            data["comments"].append(comment_info)

    db.close()
    return data

def delete_comment(id_user, id_comment):
    """
    delete a comment from the database
    """

    if not check_comment_owner(id_user, id_comment):
        return "not_comment_owner"

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM comments WHERE id_comment = ?", (id_comment,))
    db.commit()
    db.close()
    return "success"

#endregion

#region messages

def get_conversations(id_user):
    """
    return all existing conversations for a user
    """

    db = sqlite3.connect("database.db")
    cursor = db.cursor()

    # get all contacts
    cursor.execute("""
    SELECT contact, "from", isread, MAX(time) AS last_entry_time
    FROM (
        SELECT "to" AS contact, "from", isread, time
        FROM messages
        WHERE "from" = ?
        
        UNION
        
        SELECT "from" AS contact, "from", isread ,time
        FROM messages
        WHERE "to" = ?
    ) AS combined_contacts
    GROUP BY contact
    ORDER BY last_entry_time DESC""", (id_user, id_user))
    contacts = cursor.fetchall()

    conv = {
        "conv":[]
    }
    for contact,msg_from,isread,last_time in contacts:

        if isread == "N" and msg_from != id_user:
            isread = "N"
        else:
            isread = "Y"

        data = {
            "id_contact":contact,
            "last_time":last_time,
            "isread": isread
        }
        contact_info = get_user_data(contact)
        data["contact"] = contact_info["displayname"]
        data["contact_picture"] = contact_info["picture"]
        conv["conv"].append(data)

    db.close()                                                                   
    return conv

def check_message_owner(id_user, id_message):
    """
    check if a user is the given message owner
    """

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    user = cursor.execute("""
    SELECT "from"
    FROM messages WHERE id_conversation = ?""", (id_message,)).fetchone()
    db.close()
    if user is not None:
        if user[0] != id_user:
            return False
        else:
            print("User is owner")
            return True
    return False

def get_conversation(id_user,id_contact):
    """
    get all messages between two users
    """

    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    user_info = get_user_data(id_user)
    contact_info = get_user_data(id_contact)
    data = {
        "id_user":id_user,
        "user": user_info["displayname"],
        "user_picture":user_info["picture"],
        "id_contact":id_contact,
        "contact": contact_info["displayname"],
        "contact_picture":contact_info["picture"],
        "messages": []
    }

    cursor.execute("""
    SELECT "from", "to", message, time, id_conversation, isread
    FROM messages
    WHERE ("from" = ? AND "to" = ?)
    OR ("from" = ? AND "to" = ?)
    ORDER BY time""",(id_user,id_contact,id_contact,id_user));
    rows = cursor.fetchall()
    for row in rows:
        message = {
            "id_message": row[4],
            "from": row[0],
            "to": row[1],
            "message": row[2],
            "time": row[3],
            "isread": row[5],
            "owner": False
        }

        if message["isread"] == "N" and message["from"] != id_user:
            message["isread"] = "N"
        else:
            message["isread"] = "Y"

        # is owner of message
        if message["from"] == id_user:
            message["owner"] = "yes"
        data["messages"].append(message)

    # set messages as read in this conv
    cursor.execute("""
    UPDATE messages
    SET isread = 'Y'
    WHERE "from" = ? AND "to" = ?
    """,(id_contact,id_user))
    db.commit()

    db.close()
    return data

def add_message(id_user,id_contact,message):
    """
    add a message in the database
    """

    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO messages("from","to",time,message,isread)
    VALUES(?,?,datetime(),?,'N')
    """,(id_user,id_contact,message))
    db.commit()
    db.close()

def delete_message(id_user, id_message):
    """
    delete a message from the database
    """

    if not check_message_owner(id_user, id_message):
        return "not_message_owner"

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM messages WHERE id_conversation = ?", (id_message,))
    db.commit()
    db.close()
    return "success"

#endregion

