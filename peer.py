import requests


TCP_PORT = 2896


def introduce():
    url = 'http://127.0.0.1:8000/add-user'
    payload = {'username': 'jalal', 'PORT': TCP_PORT}
    response = requests.post(url, json=payload)
    print(response.text)


def get_list_users():
    url = 'http://127.0.0.1:8000/users'
    response = requests.get(url)

    print(response.text)


def get_user_ip(username):
    url = f'http://127.0.0.1:8000/user/{username}'
    response = requests.get(url)

    if response.status_code == 404:
        print("INVALID USERNAME!")
        return
    
    info = response.json() 
    print(info['IP'], info['PORT'])

introduce()
get_list_users()
get_user_ip('ali')