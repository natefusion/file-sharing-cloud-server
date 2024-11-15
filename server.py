##WORK IN PROGRESS. I STILL HAVE TO DEBUG THE CODE BUT IT CONNECTS BETWEEN THE SERVER AND CLIENT
##client_host = '34.71.63.74' NOT '127.0.0.1'. '34.71.63.74 is the external IP for (my) Google Cloud instance. 127.0.0.1 was the local IP

import socket
import threading
import os
import hashlib
import time
import pickle

client_host = '34.71.63.74'
port = 3300
BUFFER_SIZE = 1024

stored_credentials = {
    "admin": "5e884898da28047151d0e56f8dc6292773603d0d3f0e8c8b70a7c9574e2e99b9"  # Hash for 'password'
}

# Global data structure for storing client information and metrics
client_connections = {}
metrics = {
    "upload_rate": [],
    "download_rate": [],
    "file_transfer_times": [],
    "system_response_times": [],  # New metric for system response time
}


def authenticate(client_socket):
    command = client_socket.recv(1024).decode()
    if command.startswith("AUTH"):
        _, username, password_hash = command.split()
        if username in stored_credentials and stored_credentials[username] == password_hash:
            client_socket.send("Authentication successful.".encode())
            return True
        else:
            client_socket.send("Authentication failed.".encode())
            return False
    return False


def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    client_connections[addr] = client_socket

    if not authenticate(client_socket):
        client_socket.close()
        del client_connections[addr]
        print(f"[DISCONNECT] {addr} disconnected due to authentication failure.")
        return

    while True:
        try:
            start_response_time = time.time()  # Track system response time

            command = client_socket.recv(1024).decode()
            if command.startswith("UPLOAD"):
                upload_file(client_socket, command)
            elif command.startswith("DOWNLOAD"):
                download_file(client_socket, command)
            elif command.startswith("DELETE"):
                delete_file(client_socket, command)
            elif command.startswith("DIR"):
                list_files(client_socket)
            elif command.startswith("SUBFOLDER"):
                handle_subfolder(client_socket, command)
            else:
                client_socket.send(f"Invalid command: {command}".encode())
        except FileNotFoundError as e:
            client_socket.send(f"Error: File not found - {e}".encode())
        except PermissionError as e:
            client_socket.send(f"Error: Permission denied - {e}".encode())
        except Exception as e:
            client_socket.send(f"Unexpected error: {e}".encode())
            print(f"[ERROR] Unexpected error: {e}")
        finally:
            client_socket.close()
            print(f"[DISCONNECT] {addr} disconnected.")

    client_socket.close()
    del client_connections[addr]
    print(f"[DISCONNECT] {addr} disconnected.")


def upload_file(client_socket, command):
    _, filename, filesize = command.split()
    filesize = int(filesize)

    start_time = time.time()
    with open(filename, "wb") as f:
        bytes_received = 0
        while bytes_received < filesize:
            data = client_socket.recv(4096)
            bytes_received += len(data)
            f.write(data)
    end_time = time.time()

    transfer_time = end_time - start_time
    upload_rate = (filesize / transfer_time) / 10 ** 6  # Convert to MB/s
    metrics["upload_rate"].append(upload_rate)
    metrics["file_transfer_times"].append(transfer_time)
    client_socket.send("File uploaded successfully.".encode())


def download_file(client_socket, command):
    _, filename = command.split()
    if not os.path.exists(filename):
        client_socket.send("File not found.".encode())
        return

    filesize = os.path.getsize(filename)
    client_socket.send(f"{filesize}".encode())

    start_time = time.time()
    with open(filename, "rb") as f:
        bytes_sent = 0
        while bytes_sent < filesize:
            data = f.read(4096)
            client_socket.send(data)
            bytes_sent += len(data)
    end_time = time.time()

    transfer_time = end_time - start_time
    download_rate = (filesize / transfer_time) / 10 ** 6  # Convert to MB/s
    metrics["download_rate"].append(download_rate)
    metrics["file_transfer_times"].append(transfer_time)


def delete_file(client_socket, command):
    _, filename = command.split()
    if not os.path.exists(filename):
        client_socket.send("File not found.".encode())
        return

    try:
        os.remove(filename)
        client_socket.send("File deleted.".encode())
    except Exception as e:
        client_socket.send(f"Error deleting file: {str(e)}".encode())


def list_files(client_socket):
    files = "\n".join(os.listdir("."))
    client_socket.send(files.encode())


def handle_subfolder(client_socket, command):
    _, operation, path = command.split()

    try:
        if operation == "create":
            if not os.path.exists(path):
                os.makedirs(path)
                client_socket.send("Subfolder created.".encode())
            else:
                client_socket.send("Subfolder already exists.".encode())
        elif operation == "delete":
            if os.path.exists(path):
                os.rmdir(path)
                client_socket.send("Subfolder deleted.".encode())
            else:
                client_socket.send("Subfolder not found.".encode())
        else:
            client_socket.send("Invalid subfolder operation.".encode())
    except Exception as e:
        client_socket.send(f"Error in subfolder operation: {str(e)}".encode())


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print("[SERVER STARTED] Listening on port 3300")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()


def save_metrics():
    with open('transfer_metrics.pkl', 'wb') as f:
        pickle.dump(metrics, f)

if __name__ == "__main__":
    start_server()
