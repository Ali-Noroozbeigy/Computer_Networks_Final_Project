import requests

def introduce():
    url = 'http://127.0.0.1:8000/add-user'
    payload = {'username': 'ali'}
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
    
    ip = response.json()['IP']
    print(ip)

get_user_ip('li')