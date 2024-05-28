import sqlite3
from datetime import datetime
import random, requests


def save_post(id_user,visibility,title,content,tags):
    """
    create a new post in the database
    visibility : 0 is public, 1 is private
    return post id
    """


    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO posts(author,visibility,title,content,created_at)
    VALUES (?,?,?,?,datetime())""",(id_user,visibility,title,content))    
    id_post = cursor.lastrowid
    db.commit()
    for tag in tags:
        cursor.execute("SELECT * FROM tags WHERE id_tag = ?",(tag,))
        if cursor.fetchone() is not None:
            cursor.execute("INSERT INTO post_tags VALUES(?,?)",(id_post,tag))
            db.commit()

    db.close()
    return id_post

db = sqlite3.connect('database.db')
cursor = db.cursor()

with open("scripts/all.txt","r") as file:
    for line in file:
        title, url = line.split('[;]')
        body = f"""
        <img src="{url}">
        """
        id_user = random.randint(2, 49)
        tags = random.sample(range(0, 49), 20)
        save_post(id_user,0,title,body,tags)

db.close()