import requests

def get_profile_picture(hash):
    url = "https://robohash.org/"+hash
    data = requests.get(url).content
    with open(f"static/pictures/{hash}.png","wb") as file:
        file.write(data)