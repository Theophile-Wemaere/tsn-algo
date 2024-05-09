names = [
    "Alice", "Bob", "Charlie", "David", "Emily", "Frank", "Grace", "Henry",
    "Isabella", "Jack", "Olivia", "William", "Sophia", "James", "Ava", "Benjamin",
    "Charlotte", "Noah", "Mia", "Lucas", "Evelyn", "Mason", "Abigail", "Elijah",
    "Amelia", "Aiden", "Elizabeth", "Logan", "Ella", "Matthew", "Sofia", "Daniel",
    "Madison", "Michael", "Chloe", "Ethan", "Harper", "Alexander", "Avery",
    "Aaliyah", "Christopher", "Scarlett", "Joseph", "Eleanor", "Andrew", "Luna",
    "Gabriel", "Layla", "Jackson", "Penelope", "Carter", "Riley", "Caleb", "Zoey",
    "Owen", "Nora", "Liam", "Mila", "Wyatt", "Stella"
]

words = [
    "computer", "smartphone", "television", "tablet", "monitor",
    "circuit", "transistor", "diode", "capacitor", "resistor",
    "battery", "charger", "speaker", "microphone", "camera",
    "sensor", "processor", "memory", "storage", "software",
    "hardware", "internet", "network", "wireless", "bluetooth",
    "signal", "frequency", "voltage", "current", "power",
    "logic gate", "microcontroller", "artificial intelligence",
    "robotics", "automation", "virtual reality", "augmented reality",
    "drone", "3D printing", "electromagnetism", "semiconductor",
    "digital", "analog", "assembly language", "operating system",
    "programming", "debugging", "electronics engineer", "innovation"
]

import sqlite3
from datetime import datetime
import random

db = sqlite3.connect('database.db')
cursor = db.cursor()

for i in range(49):
    data = (i,words[i])
    sql = "INSERT INTO tags VALUES (?,?)"
    cursor.execute(sql,data)
    db.commit()


for i in range(50):
    username = names[i]
    email = username + "@gmail.com" 
    password = "$argon2id$v=19$m=65536,t=3,p=4$Xnxa1KGOvUOzg31KMxTHKw$NA9ZTeYaNo9kk3NBaXo1V0tNiVdAFlVqyRDlnZG/jaM"
    # todo : handle already exisiting email
    data = (i,username, email, password, "user", "X", "Y")
    sql = """INSERT INTO users (id_user,username, email, password, role, gender, notification) 
    VALUES (?,?, ?, ?, ?, ?, ?)"""
    cursor.execute(sql,data)
    db.commit()

    numbers = random.sample(range(0, 49), 5)
    for n in numbers:
        sql = "INSERT INTO user_tags VALUES(?,?)"
        cursor.execute(sql,(i,n))
    db.commit()



db.close()