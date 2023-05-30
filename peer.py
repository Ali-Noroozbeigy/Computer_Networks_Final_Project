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


def remove_user(username):
    url = 'http://127.0.0.1:8000/remove/'
    payload = {'username': username}
    requests.post(url, json=payload)



def wait_for_peers_to_call():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind((HOST, UDP_PORT))
    
    while True:
        print('wait for peers to call...')
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

    send_done = False
    while not send_done:
        print("Sending File...")
        file_size = os.path.getsize('sample.txt')
        conn.send(str(file_size).encode('utf-8'))

        with open('sample.txt', 'rb') as txt:
            conn.send(txt.read(file_size))
        
        if conn.recv(10).decode('utf-8') == 'OK':
            send_done = True
            tcp_socket.close()
            print("File Sent.")


def call_user(ip, port, data_type: str):
    if data_type == 'TEXT':
        return request_text(ip, port, data_type) 
        

def request_text(ip, port, data_type):
    print("Wait for user to accept...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_type = data_type.encode('utf-8')
    udp_socket.sendto(data_type, (ip, int(port)))

    udp_socket.settimeout(15)
    try:
        data, addr = udp_socket.recvfrom(10)
    except socket.timeout:
        print("it seems that peer is offline. try other peers.")
        return False
    data = data.decode('utf-8')
    if data == "DECLINED":
        print("Your request declined!")
        return False
    udp_socket.close()
    print("Request Accepted!")
    print("Establishing Connection...")
    tcp = int(data)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((ip, tcp))
    print("Connection Established.")
    size = tcp_socket.recv(4)
    recv_done = False
    while not recv_done:
        try:
            text = tcp_socket.recv(int(size.decode('utf-8')))
            with open('received.txt', 'w') as rcv:
                rcv.write(text.decode('utf-8'))
            tcp_socket.send('OK'.encode('utf-8'))
            print("File received.")
            recv_done = True
        except socket.error as e:
            tcp_socket.send("ERROR".encode('utf-8'))
    return True


introduced = False
while not introduced:
    introduced = introduce()

choice = input('Do you want to share or get file?[s/g]')
if choice == 's':
    wait_for_peers_to_call()
else:
    find_peer = False
    while not find_peer:
        get_list_users()
        target = input('Please enter a username to start: ')
        ip, port = get_user_ip(target)
        find_peer = call_user(ip, port, 'TEXT')
        if not find_peer:
            remove_user(target)