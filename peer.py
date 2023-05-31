import requests
import socket
import os
from PIL import Image
from time import sleep

UDP_PORT = 2896
TCP_PORT = 8400
HOST = '127.0.0.1'
CHUNK_SIZE = 1024


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
                udp_socket.sendto(b'OK', addr)
                send_picture(udp_socket, addr)
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


def send_picture(udp_socket: socket.socket, addr):
    im = Image.open("./sample_pic.jpg")
    im_bytes = im.tobytes()

    x = im.size[0].to_bytes(4, byteorder='big')
    y = im.size[1].to_bytes(4, byteorder='big')

    udp_socket.sendto(x, addr)
    sleep(0.01)
    udp_socket.sendto(y, addr)
    sleep(0.01)

    chunks = [im_bytes[i:i+CHUNK_SIZE] for i in range(0, len(im_bytes), CHUNK_SIZE)]

    for i, chunk in enumerate(chunks):
        udp_socket.sendto(b'1', addr)
        seq_num = i.to_bytes(4, byteorder='big')
        udp_socket.sendto(seq_num + chunk, addr)
        print(f'send chunk {int.from_bytes(seq_num, byteorder="big")}')
        sleep(0.01)
    udp_socket.sendto(b'0', addr)



def call_user(ip, port, data_type: str):
    print("Wait for user to accept...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(data_type.encode('utf-8'), (ip, int(port)))

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
    
    print("Request Accepted!")
    udp_socket.settimeout(None)
    if data_type == 'TEXT':
        return request_text(ip, data)
    else:
        request_image(udp_socket)
        

def request_text(ip, data):
    
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


def request_image(udp_socket: socket.socket):
    
    x = int.from_bytes(udp_socket.recvfrom(4)[0], byteorder='big')
    y = int.from_bytes(udp_socket.recvfrom(4)[0], byteorder='big')
    
    print(x,y)

    received_chunks = {}
    
    finished = False

    while not finished:
        data, addr = udp_socket.recvfrom(1)
        if data.decode('utf-8') == '0':
            finished = True
            continue
        data, addr = udp_socket.recvfrom(1028)
        seq_number = int.from_bytes(data[:4], byteorder='big')
        chunk = data[4:]
        received_chunks[seq_number] = chunk
        #print(f"chunk {seq_number} received!")
    
    sorted_chunks = [received_chunks[i] for i in range(len(received_chunks))]
    image_bytes = b''.join(sorted_chunks)

    im = Image.frombytes('RGB', (x,y), image_bytes)
    im.save('received_img.jpg')




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
        data_type = 'TEXT' if input('Enter type of data: [T/P]') == 'T' else 'PICTURE'
        find_peer = call_user(ip, port, data_type)
        if not find_peer:
            remove_user(target)