import requests


UDP_PORT = 2896
HOST = '127.0.0.1'


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


def wait_for_peers_to_call():
    import socket

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind((HOST, UDP_PORT))

    print('wait for peers to call...')
    
    while True:
        data, addr = udp_socket.recvfrom(1024)
        agree = input(f'New Connection From {addr}, Agree? [Y/n]')

        if agree == 'Y':
            pass
        else:
            continue




introduce()
get_list_users()
get_user_ip('ali')