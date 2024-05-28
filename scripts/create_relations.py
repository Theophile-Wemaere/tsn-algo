import sqlite3
import random
from alive_progress import alive_bar

db = sqlite3.connect("database.db")
cursor = db.cursor()

with alive_bar(49) as bar:
    for user in range(1,50):
    
        while True:
            target = random.randint(1,49)
            if target != user:
                break
        cursor.execute("""
        INSERT INTO relations(followed,follower)
        VALUES (?,?)""",(user,target))
        db.commit()


        while True:
            target = random.randint(1,49)
            if target != user:
                break
        cursor.execute("""
        INSERT INTO relations(followed,follower)
        VALUES (?,?)""",(target,user))
        db.commit()
        bar()

db.close()