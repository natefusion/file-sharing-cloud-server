##WORK IN PROGRESS. I STILL HAVE TO DEBUG THE CODE BUT IT CONNECTS BETWEEN THE SERVER AND CLIENT
##client_host = '34.71.63.74' NOT '127.0.0.1'. '34.71.63.74 is the external IP for (my) Google Cloud instance. 127.0.0.1 was the local IP

import socket
import os
import time
import hashlib

client_host = '34.71.63.74'
port = 3300
BUFFER_SIZE = 1024


def send_command(client_socket, command):
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    print(response)


def upload_file(client_socket, filename):
    try:
        if not os.path.exists(filename):
            print("File does not exist.")
            return

        filesize = os.path.getsize(filename)
        send_command(client_socket, f"UPLOAD {filename} {filesize}")

        with open(filename, "rb") as f:
            bytes_sent = 0
            start_time = time.time()
            while bytes_sent < filesize:
                data = f.read(4096)
                client_socket.send(data)
                bytes_sent += len(data)
            end_time = time.time()

        transfer_time = end_time - start_time
        upload_rate = (filesize / transfer_time) / 10 ** 6  # Convert to MB/s
        print(f"Upload completed in {transfer_time:.2f} seconds.")
        print(f"Upload rate: {upload_rate:.2f} MB/s")
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except PermissionError:
        print(f"Error: Permission denied to upload {filename}.")
    except Exception as e:
        print(f"Unexpected error during file upload: {e}")
# Similar enhancements can be made to other functions such as download_file(), delete_file(), etc.

def download_file(client_socket, filename):
    try:
        # Request the file from the server
        send_command(client_socket, f"DOWNLOAD {filename}")
        response = client_socket.recv(4096).decode()

        # Check if the server sent a valid file size (indicating the file exists)
        if response.isdigit():
            filesize = int(response)
            with open(filename, "wb") as f:
                bytes_received = 0
                start_time = time.time()
                while bytes_received < filesize:
                    data = client_socket.recv(4096)
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
            # Handle the server's error response (e.g., "File not found.")
            print(f"Server response: {response}")

    except FileNotFoundError:
        print(f"Error: Unable to save downloaded file. Check if the directory exists.")
    except PermissionError:
        print(f"Error: Permission denied while saving {filename}.")
    except ConnectionError as ce:
        print(f"Download failed: {ce}")
    except Exception as e:
        print(f"Unexpected error during file download: {e}")


def delete_file(client_socket, filename):
    try:
        # Send delete command to the server
        send_command(client_socket, f"DELETE {filename}")
        response = client_socket.recv(4096).decode()

        # Check if the server returned an error message
        if "Error" in response or "not found" in response:
            print(f"Server response: {response}")
        else:
            print(response)  # Confirm successful deletion

    except ConnectionError:
        print("Error: Lost connection to server during delete operation.")
    except Exception as e:
        print(f"Unexpected error during file deletion: {e}")


def create_subfolder(client_socket, folder_name):
    send_command(client_socket, f"SUBFOLDER create {folder_name}")


def delete_subfolder(client_socket, folder_name):
    send_command(client_socket, f"SUBFOLDER delete {folder_name}")


def authenticate(client_socket):
    username = input("Enter username: ")
    password = input("Enter password: ")
    # Hash the password before sending it (don't send plain text password)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    send_command(client_socket, f"AUTH {username} {password_hash}")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((client_host, port))

    # Implement authentication
    # authenticate(client_socket)

    # Example usage for file upload, download and performance evaluation
    upload_file(client_socket, "example.txt")
    download_file(client_socket, "example.txt")

    # Send command to list files
    send_command(client_socket, "DIR")

    # New functionalities
    delete_file(client_socket, "example.txt")
    create_subfolder(client_socket, "new_folder")
    delete_subfolder(client_socket, "new_folder")

    client_socket.close()


if __name__ == "__main__":
    main()
