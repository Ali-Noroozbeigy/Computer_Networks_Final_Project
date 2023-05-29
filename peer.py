import requests
import socket
import os


UDP_PORT = 2896
TCP_PORT = 8400
HOST = '127.0.0.1'


def introduce():
    url = 'http://127.0.0.1:8000/add-user'
    payload = {'username': 'jalal', 'PORT': UDP_PORT}
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
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind((HOST, UDP_PORT))

    print('wait for peers to call...')
    
    while True:
        data, addr = udp_socket.recvfrom(1024)
        data = data.decode('utf-8')
        agree = input(f'New Connection From {addr}, asking for {data}, Agree? [Y/n]')

        if agree == 'Y':
            if data == 'TEXT':
                port_as_byte = TCP_PORT.to_bytes(2, byteorder='big')
                udp_socket.sendto(port_as_byte)
                listen_for_tcp()
            else:
                print("THE connection wants photo :(")
        else:
            continue


def listen_for_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST, TCP_PORT))
    tcp_socket.listen()

    conn, addr = tcp_socket.accept()
    print(f"New TCP Connection from {addr} for TEXT")
    file_size = os.path.getsize('sample.txt')
    conn.send(file_size.to_bytes(4, byteorder='big'))

    with open('sample.txt', 'rb') as txt:
        conn.send(txt.read(file_size))
    
    tcp_socket.close()



introduce()
get_list_users()
get_user_ip('ali')