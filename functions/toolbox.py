import requests

def get_profile_picture(hash):
    url = "https://robohash.org/"+hash
    data = requests.get(url).content
    with open(f"static/pictures/{hash}.png","wb") as file:
        file.write(data)

def allowed_file(filename):
  ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# ALGORITHM USED TO SORT POST AND USERS RECOMMANDATIONS
def reverse_list(array):

    new_array = []
    for _ in range(len(array)):
        new_array.append(array.pop(-1))
    return new_array

def merge(left_array, right_array):
    merged_array = []

    while left_array and right_array:
        if left_array[0][0] <= right_array[0][0]:
            merged_array.append(left_array[0])
            left_array.pop(0)
        else:
            merged_array.append(right_array[0])
            right_array.pop(0)

    while left_array:
        merged_array.append(left_array[0])
        left_array.pop(0)
    while right_array:
        merged_array.append(right_array[0])
        right_array.pop(0)
    
    return merged_array

def merge_sort_recursive(array):
    if len(array) <= 1:
        return array
    
    middle_index = len(array) // 2
    left_array = array[:middle_index]
    right_array = array[middle_index:]

    left_array = merge_sort_recursive(left_array)
    right_array = merge_sort_recursive(right_array)

    return merge(left_array, right_array)