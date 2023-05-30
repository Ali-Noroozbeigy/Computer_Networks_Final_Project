import requests
import socket
import os


UDP_PORT = 2896
TCP_PORT = 8400
HOST = '127.0.0.1'


def introduce():
    username = input('Please Introduce Yourself: ')
    url = 'http://127.0.0.1:8000/add-user'
    payload = {'username': username, 'PORT': UDP_PORT}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Introduction Successful.")
        return True
    elif response.status_code == 409:
        print('username exists. select another username.')
        return False
    else:
        print(response.text)
        exit()


def get_list_users():
    url = 'http://127.0.0.1:8000/users'
    response = requests.get(url)

    print(f'here is the list of users:\n{response.text}')


def get_user_ip(username):
    url = f'http://127.0.0.1:8000/user/{username}'
    response = requests.get(url)

    if response.status_code == 404:
        print("INVALID USERNAME!")
        return
    
    info = response.json() 
    return(info['IP'], info['PORT'])


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
                udp_socket.sendto(str(TCP_PORT).encode('utf-8'), addr)
                listen_for_tcp()
            else:
                print("THE connection wants photo :(")
        else:
            udp_socket.sendto(b'DECLINED', addr)


def listen_for_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST, TCP_PORT))
    tcp_socket.listen()

    conn, addr = tcp_socket.accept()
    print(f"New TCP Connection from {addr} for TEXT")
    file_size = os.path.getsize('sample.txt')
    conn.send(str(file_size).encode('utf-8'))

    with open('sample.txt', 'rb') as txt:
        conn.send(txt.read(file_size))
    
    tcp_socket.close()


def call_user(ip, port, data_type: str):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_type = data_type.encode('utf-8')
    udp_socket.sendto(data_type, (ip, int(port)))

    data, addr = udp_socket.recvfrom(10)
    data = data.decode('utf-8')
    if data == "DECLINED":
        print("Your request declined!")
        return
    udp_socket.close()
    tcp = int(data)
    print(tcp)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((ip, tcp))

    size = tcp_socket.recv(4)
    text = tcp_socket.recv(int(size.decode('utf-8')))
    with open('received.txt', 'w') as rcv:
        rcv.write(text.decode('utf-8'))


introduced = False
while not introduced:
    introduced = introduce()

choice = input('Do you want to share or get file?[s/g]')
if choice == 's':
    wait_for_peers_to_call()
else:
    get_list_users()
    target = input('Please enter a username to start: ')
    ip, port = get_user_ip(target)
    call_user(ip, port, 'TEXT')