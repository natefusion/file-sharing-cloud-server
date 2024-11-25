import socket
import os
import time
import hashlib
from pathlib import Path

client_host = '35.229.101.87'
port = 3389
BUFFER_SIZE = 4096

def authenticate(client_socket):
    # Prompt for username and password before generating the hash.
    #Username "admin"
    #Password is "password"
    username = input("Enter username: ")
    password = input("Enter password: ")

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Send the authentication command with the username and hashed password
    client_socket.send(f"AUTH {username} {password_hash}".encode())

    ack = client_socket.recv(BUFFER_SIZE).decode()
    if ack.startswith('ACK'):
        return True
    else:
        print('Error: ', ack.split('\n')[1:])
        return False


def send_command(client_socket, command):  # MH
    client_socket.send(command.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    return response  # MH: Return the server response for flexibility


def validate_command(message):
    is_valid = None
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
            if cmd[2].startswith('server://'):
                handle_err(Path(cmd[3]).parent.is_dir(), 'Parent directory does not exist')

            elif cmd[3].startswith('server://'):
                handle_err(Path(cmd[2]).is_file(), 'File does not exist')
        else:
            if cmd[1].startswith('server://'):
                if not Path(cmd[2]).parent.is_dir():
                    is_valid = False
                    error_message = 'Parent directory does not exist'
                elif Path(cmd[2]).is_file():
                    is_valid = False
                    error_message = 'File already exists'
                else:
                    is_valid = True
            elif cmd[2].startswith('server://'):
                handle_err(Path(cmd[1]).is_file(), 'File, does not exist')

    elif 'rm' == cmd[0]:
        # [0] [1] [2]
        # rm  -d   a
        # rm  a
        if len(cmd) == 1:
            handle_err(False, f'Expected 3 args, but got 1 arg')
        else:
            if cmd[1] == '-d':
                handle_err(len(cmd) == 3, f'Expected 3 args, but got {len(cmd)} args')
            else:
                handle_err(len(cmd) == 2, f'Expected 2 args, but got {len(cmd)} args')
    elif 'ls' == cmd[0]:
        # [0] [1]
        # ls   a
        handle_err(len(cmd) == 2, f'Expected 2 args, but got {len(cmd)} args')
    elif 'mkdir' == cmd[0]:
        handle_err(len(cmd) == 2, f'Expected 2 args, but got {len(cmd)} args')

    assert(is_valid != None)
    if is_valid:
        assert(error_message == None)
    else:
        assert(error_message != None)

    return is_valid, error_message


def upload_file(client_socket, filepath):  # MH
    if not os.path.exists(filepath):
        print("File does not exist.")
        return

    filesize = os.path.getsize(filepath)
    client_socket.send(str(filesize).encode())  # MH: Send the filesize as the first message

    ack = client_socket.recv(BUFFER_SIZE).decode()

    if not ack.startswith('ACK'):
        return

    with open(filepath, "rb") as f:
        bytes_sent = 0
        start_time = time.time()
        while bytes_sent < filesize:
            data = f.read(BUFFER_SIZE)
            client_socket.send(data)
            bytes_sent += len(data)
            print(f'\x1b[A\x1b[2KUpload progress: {bytes_sent/filesize*100:.0f}%')
        end_time = time.time()

    transfer_time = end_time - start_time
    upload_rate = (filesize / transfer_time) / 10**6  # Convert to MB/s
    print(f"Upload completed in {transfer_time:.2f} seconds.")
    print(f"Upload rate: {upload_rate:.2f} MB/s")


def download_file(client_socket, filepath):  # MH
    response = client_socket.recv(BUFFER_SIZE).decode()
    filesize = int(response)

    client_socket.send('ACK'.encode())
            
    with open(filepath, "wb") as f:
        bytes_received = 0
        start_time = time.time()
        while bytes_received < filesize:
            data = client_socket.recv(BUFFER_SIZE)
            bytes_received += len(data)
            f.write(data)
            print(f'\x1b[A\x1b[2KDownload progress: {bytes_received/filesize*100:.0f}%')
        end_time = time.time()

    transfer_time = end_time - start_time
    download_rate = (filesize / transfer_time) / 10**6  # Convert to MB/s

    print(f"Download completed in {transfer_time:.2f} seconds.")
    print(f"Download rate: {download_rate:.2f} MB/s")


def main():  # MH
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((client_host, port))

        if not authenticate(client_socket):
            quit()
            
        print("Connected to server.")

        while True:
            command = input("> ")
            if command == 'q':
                client_socket.send('q'.encode())
                print("Exiting...")
                break

            is_valid, error_message = validate_command(command)
            if is_valid:
                response = send_command(client_socket, command)  # MH

                if response.startswith("ACK"):  # MH: Handle commands based on the server's ACK
                    client_socket.send('ACK'.encode())

                    words = command.split(' ')
                    if words[0] == 'cp':
                        if words[1] == '-f':
                            arg1 = words[2]
                            arg2 = words[3]
                        else:
                            arg1 = words[1]
                            arg2 = words[2]
                        
                        if arg1.startswith('server://'):
                            download_file(client_socket, arg2)
                        else:
                            upload_file(client_socket, arg1)
                    elif command.startswith("ls"):  # MH
                        data = client_socket.recv(BUFFER_SIZE).decode()
                        print(data)
                    elif command.startswith("rm"):  # MH
                        print("rm acknowledged, no further action.")  # MH
                    elif command.startswith("mkdir"):  # MH
                        print("mkdir acknowledged, no further action.")  # MH
                    elif response.startswith("NACK"):  # MH
                        print("Command not acknowledged by the server.")  # MH
                    else:
                        print(f"Unexpected server response: {response}")  # MH
                else:
                    print('Server error:', response.split('\n')[1:])
            else:
                print('Client Error: ', error_message)
                        

if __name__ == "__main__":
    main()
