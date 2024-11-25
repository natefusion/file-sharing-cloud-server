import socket
import os
import time
import hashlib

client_host = '35.229.101.87'  # Replace with the external IP address of the running instance
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
    send_command(client_socket, f"AUTH {username} {password_hash}")


def send_command(client_socket, command):  # MH
    client_socket.send(command.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    return response  # MH: Return the server response for flexibility


def upload_file(client_socket, filepath):  # MH
    try:
        if not os.path.exists(filepath):
            print("File does not exist.")
            return

        filesize = os.path.getsize(filepath)
        client_socket.send(str(filesize).encode())  # MH: Send the filesize as the first message

        ack = client_socket.recv(BUFFER_SIZE).decode()

        if ack != 'ACK':
            return

        with open(filepath, "rb") as f:
            bytes_sent = 0
            start_time = time.time()
            while bytes_sent < filesize:
                data = f.read(BUFFER_SIZE)
                client_socket.send(data)
                bytes_sent += len(data)
            end_time = time.time()

        transfer_time = end_time - start_time
        upload_rate = (filesize / transfer_time) / 10**6  # Convert to MB/s
        print(f"Upload completed in {transfer_time:.2f} seconds.")
        print(f"Upload rate: {upload_rate:.2f} MB/s")
    except Exception as e:
        print(f"Error during file upload: {e}")


def download_file(client_socket, filepath):  # MH
    try:
        response = client_socket.recv(BUFFER_SIZE).decode()
        if response.isdigit():
            filesize = int(response)
            socket.send('ACK'.encode())
            
            with open(filepath, "wb") as f:
                bytes_received = 0
                start_time = time.time()
                while bytes_received < filesize:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        raise ConnectionError("Connection lost during file download.")
                    bytes_received += len(data)
                    f.write(data)
                end_time = time.time()

            transfer_time = end_time - start_time
            download_rate = (filesize / transfer_time) / 10**6  # Convert to MB/s
            print(f"Download completed in {transfer_time:.2f} seconds.")
            print(f"Download rate: {download_rate:.2f} MB/s")
        else:
            print(f"Server response: {response}")
    except Exception as e:
        print(f"Error during file download: {e}")


def main():  # MH
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((client_host, port))
        print("Connected to server.")

        while True:
            command = input("> ")
            if command == 'q':
                print("Exiting...")
                break

            response = send_command(client_socket, command)  # MH

            if response.startswith("ACK"):  # MH: Handle commands based on the server's ACK
                client_socket.send('ACK'.encode())

                words = command.split(' ')
                if words[0] == 'cp':
                    if words[1].startswith('server://'):
                        download_file(client_socket, words[3])
                    else:
                        upload_file(client_socket, words[1])
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


if __name__ == "__main__":
    main()
