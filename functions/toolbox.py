import requests

def get_profile_picture(hash):
    url = "https://robohash.org/"+hash
    data = requests.get(url).content
    with open(f"static/pictures/{hash}.png","wb") as file:
        file.write(data)

def allowed_file(filename):
  ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS