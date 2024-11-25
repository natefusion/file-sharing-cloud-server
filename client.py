import socket
import os
import time
import hashlib

client_host = '34.71.63.74'  # Replace with the external IP address of the running instance
port = 3300
BUFFER_SIZE = 1024

def send_command(client_socket, command):  # MH
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    return response  # MH: Return the server response for flexibility


def upload_file(client_socket, filepath):  # MH
    try:
        if not os.path.exists(filepath):
            print("File does not exist.")
            return

        filesize = os.path.getsize(filepath)
        client_socket.send(str(filesize).encode())  # MH: Send the filesize as the first message

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
        response = client_socket.recv(4096).decode()
        if response.isdigit():
            filesize = int(response)
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

            if response == "ACK":  # MH: Handle commands based on the server's ACK
                if command.startswith("cp server://"):  # MH
                    filepath = command.split(" ")[1]
                    dest = command.split(" ")[2]
                    download_file(client_socket, dest)
                elif command.startswith("cp") and "server://" in command:  # MH
                    src = command.split(" ")[1]
                    upload_file(client_socket, src)
                elif command.startswith("ls"):  # MH
                    print(client_socket.recv(4096).decode())  # MH: Print server response
                elif command.startswith("rm"):  # MH
                    print("rm acknowledged, no further action.")  # MH
                elif command.startswith("mkdir"):  # MH
                    print("mkdir acknowledged, no further action.")  # MH
            elif response == "NACK":  # MH
                print("Command not acknowledged by the server.")  # MH
            else:
                print(f"Unexpected server response: {response}")  # MH


if __name__ == "__main__":
    main()
