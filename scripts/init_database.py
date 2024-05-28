names = [
    "admin","Alice", "Bob", "Charlie", "David", "Emily", "Frank", "Grace", "Henry",
    "Isabella", "Jack", "Olivia", "William", "Sophia", "James", "Ava", "Benjamin",
    "Charlotte", "Noah", "Mia", "Lucas", "Evelyn", "Mason", "Abigail", "Elijah",
    "Amelia", "Aiden", "Elizabeth", "Logan", "Ella", "Matthew", "Sofia", "Daniel",
    "Madison", "Michael", "Chloe", "Ethan", "Harper", "Alexander", "Avery",
    "Aaliyah", "Christopher", "Scarlett", "Joseph", "Eleanor", "Andrew", "Luna",
    "Gabriel", "Layla", "Jackson", "Penelope", "Carter", "Riley", "Caleb", "Zoey",
    "Owen", "Nora", "Liam", "Mila", "Wyatt"
]

surnames = [
    "3000","Smith", "Johnson", "Williams", "Brown", "Jones",
    "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
    "Moore", "Anderson", "Taylor", "Thomas", "Hernandez",
    "Walker", "Moore", "Allen", "Young", "King",
    "Wright", "Lopez", "Scott", "Robinson", "Lewis",
    "Lee", "Walker", "Hall", "Allen", "Carter",
    "Nguyen", "Campbell", "Mitchell", "Martin", "Hernandez",
    "Clark", "Rodriguez", "Lewis", "Robinson", "Walker",
    "Perez", "Sanchez", "Young", "Moore", "Allen",
    "Nelson", "Garcia", "Wright", "Lopez"
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
import random, requests

db = sqlite3.connect('database.db')
cursor = db.cursor()

with open('scripts/create.sql') as f:
    db.executescript(f.read())

# create default tags
for word in words:
    data = (word,)
    sql = "INSERT INTO tags(name) VALUES (?)"
    cursor.execute(sql,data)
    db.commit()

hashs = []

for i in range(50):
    username = names[i]
    email = username + "@local.com"
    displayname = f"{names[i]} {surnames[i].upper()}"
    password = "default"
    
    while True:
        hash = str(random.getrandbits(128))
        if hash not in hashs:
            hashs.append(hash)
            break
    
    url = "https://robohash.org/"+hash
    data = requests.get(url).content
    with open(f"static/pictures/{hash}.png","wb") as file:
        file.write(data)

    data = (email, username, displayname, password,hash)
    sql = """
    INSERT INTO users(email, username, displayname, password, role, created_at, last_update, gender, notification, location, picture) 
    VALUES (?, ?, ?, ?, 'user', date(), datetime(), 'X', 'N', 'The Internet',?)"""
    cursor.execute(sql,data)
    db.commit()

    numbers = random.sample(range(0, 49), 5)
    for n in numbers:
        sql = "INSERT INTO user_tags VALUES(?,?)"
        cursor.execute(sql,(i,n))
    db.commit()

db.close()
