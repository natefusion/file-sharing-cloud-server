##WORK IN PROGRESS. I STILL HAVE TO DEBUG THE CODE BUT IT CONNECTS BETWEEN THE SERVER AND CLIENT
##client_host = '34.71.63.74' NOT '127.0.0.1'. '34.71.63.74 is the external IP for (my) Google Cloud instance. 127.0.0.1 was the local IP

import socket
import threading
import os
import time
import pickle
from pathlib import Path

host = '10.142.0.2'
port = 3389
BUFFER_SIZE = 4096

SERVER_ROOT = Path('/home/nthnpiel/server/')

stored_credentials = {
    "admin": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # Hash for 'password'
}

# Global data structure for storing client information and metrics
client_connections = {}
metrics = {
    "upload_rate": [],
    "download_rate": [],
    "file_transfer_times": [],
    "system_response_times": [],  # New metric for system response time
}

class Command:
    def __init__(self, name, arg1, arg2, flag):
        self.name = name
        self.flag = flag
        self.arg1 = arg1
        self.arg2 = arg2


def authenticate(client_socket):
    command = client_socket.recv(BUFFER_SIZE).decode()
    if command.startswith("AUTH"):
        _, username, password_hash = command.split()
        if username in stored_credentials and stored_credentials[username] == password_hash:
            client_socket.send("ACK".encode())
            return True
        else:
            client_socket.send("NACK\nAuthentication failed.".encode())
            return False
    return False


def validate_command(message):
    is_valid = None
    command = None
    error_message = None
    
    def handle_err(cond, msg):
        nonlocal is_valid
        nonlocal error_message
        if cond:
            is_valid = True
        else:
            is_valid = False
            error_message = msg

    cmd = message.split(' ')
    if 'cp' == cmd[0]:
        # [0] [1] [2] [3]
        # cp  -f   a   b
        # cp   a   b

        if cmd[1] == '-f':
            command = Command(cmd[0], cmd[2], cmd[3], cmd[1])
            if cmd[2].startswith('server://'):
                handle_err(SERVER_ROOT.joinpath(cmd[2][9:]).is_file(), 'File does not exist')
            elif cmd[3].startswith('server://'):
                handle_err(SERVER_ROOT.joinpath(cmd[3][9:]).parent.is_dir(), 'Parent directory does not exist')
        else:
            command = Command(cmd[0], cmd[1], cmd[2], None)
            if cmd[1].startswith('server://'):
                handle_err(SERVER_ROOT.joinpath(cmd[1][9:]).is_file(), 'File, does not exist')
            elif cmd[2].startswith('server://'):
                if not SERVER_ROOT.joinpath(cmd[2][9:]).parent.is_dir():
                    is_valid = False
                    error_message = 'Parent directory does not exist'
                elif SERVER_ROOT.joinpath(cmd[2][9:]).is_file():
                    is_valid = False
                    error_message = 'File already exists'
                else:
                    is_valid = True
    elif 'rm' == cmd[0]:
        # [0] [1] [2]
        # rm  -d   a
        # rm  a
        if cmd[1] == '-d':
            command = Command(cmd[0], cmd[2], None, cmd[1])
            handle_err(len(os.listdir(SERVER_ROOT.joinpath(cmd[2]))) == 0, 'Directory is not empty')
        else:
            command = Command(cmd[0], cmd[1], None, None)
            handle_err(SERVER_ROOT.joinpath(cmd[1]).is_file(), 'File does not exist')
    elif 'ls' == cmd[0]:
        # [0] [1]
        # ls   a
        command = Command(cmd[0], cmd[1], None, None)
        handle_err(SERVER_ROOT.joinpath(cmd[1]).is_dir(), 'Not a directory')
    elif 'mkdir' == cmd[0]:
        command = Command(cmd[0], cmd[1], None, None)
        path = SERVER_ROOT.joinpath(cmd[1])
        a = path.parent.is_dir()
        b = not path.is_dir()
        if a and b:
            is_valid = True
        elif not a:
            is_valid = False
            error_message = 'Parent directory does not exist'
        elif not b:
            is_valid = False
            error_message = 'directory already exists'

    print(is_valid, error_message)
    assert(is_valid != None)
    assert(command != None)
    if is_valid:
        assert(error_message == None)
    else:
        assert(error_message != None)

    return is_valid, command, error_message


def execute_command(socket, cmd):
    if 'cp' == cmd.name:
        if cmd.arg1.startswith('server://'):
            copy_file_to_client(socket, SERVER_ROOT.joinpath(cmd.arg1[9:]))
        else:
            copy_file_to_server(socket, SERVER_ROOT.joinpath(cmd.arg2[9:]))
    elif 'rm' == cmd.name:
        if cmd.flag == '-d':
            os.rmdir(SERVER_ROOT.joinpath(cmd.arg1))
        else:
            os.remove(SERVER_ROOT.joinpath(cmd.arg1))
    elif 'ls' == cmd.name:
        files = '\n'.join(os.listdir(SERVER_ROOT.joinpath(cmd.arg1)))
        if files == '':
            files = 'Directory is empty'
        socket.send(files.encode())
    elif 'mkdir' == cmd.name:
        os.makedirs(SERVER_ROOT.joinpath(cmd.arg1))
    

def send_ack(socket):
    socket.send('ACK'.encode())

    
def send_nack(socket, msg):
    socket.send(f'NACK\n{msg}'.encode())

    
def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    client_connections[addr] = client_socket

    if not authenticate(client_socket):
        client_socket.close()
        del client_connections[addr]
        print(f"[DISCONNECT] {addr} disconnected due to authentication failure.")
        return

    while True:
        start_response_time = time.time()  # Track system response time

        message = client_socket.recv(BUFFER_SIZE).decode()

        if message == 'q':
            break
            
        is_valid, command, error_message = validate_command(message)

        if is_valid:
            send_ack(client_socket)
            data = client_socket.recv(BUFFER_SIZE).decode()
            if data.startswith('ACK'):
                execute_command(client_socket, command)
        else:
            send_nack(client_socket, error_message)
                    
        
    client_socket.close()
    del client_connections[addr]
    print(f"[DISCONNECT] {addr} disconnected.")


def copy_file_to_server(client_socket, filename):
    start_time = time.time()
    
    filesize = client_socket.recv(BUFFER_SIZE).decode()
    filesize = int(filesize)

    send_ack(client_socket)
    
    with open(filename, "wb") as f:
        bytes_received = 0
        while bytes_received < filesize:
            data = client_socket.recv(BUFFER_SIZE)
            bytes_received += len(data)
            f.write(data)
    end_time = time.time()

    transfer_time = end_time - start_time
    upload_rate = (filesize / transfer_time) / 10 ** 6  # Convert to MB/s
    metrics["upload_rate"].append(upload_rate)
    metrics["file_transfer_times"].append(transfer_time)


def copy_file_to_client(client_socket, filename):
    filesize = os.path.getsize(filename)
    client_socket.send(f"{filesize}".encode())

    ack = client_socket.recv(BUFFER_SIZE).decode()
    if not ack.startswith('ACK'):
        return

    start_time = time.time()
    with open(filename, "rb") as f:
        bytes_sent = 0
        while bytes_sent < filesize:
            data = f.read(BUFFER_SIZE)
            client_socket.send(data)
            bytes_sent += len(data)
    end_time = time.time()

    transfer_time = end_time - start_time
    download_rate = (filesize / transfer_time) / 10 ** 6  # Convert to MB/s
    metrics["download_rate"].append(download_rate)
    metrics["file_transfer_times"].append(transfer_time)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("[SERVER STARTED] Listening on port 3300")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

    server_socket.close()


def save_metrics():
    with open('transfer_metrics.pkl', 'wb') as f:
        pickle.dump(metrics, f)

if __name__ == "__main__":
    start_server()
