import socket
import sys

client_host = '127.0.0.1'
server_host = '127.0.0.1'
port = 3300 # 3389

BUFFER_SIZE = 1024

def server():
    dashes = '----> '
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_tcp:
        server_tcp.bind((server_host, port))

        while True:
            server_tcp.listen(6)
            print('[*] Waiting for connection')

            connection, addr = server_tcp.accept()
            with connection:
                print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
                while True:
                    data = connection.recv(BUFFER_SIZE)

                    if not data:
                        break
                    else:
                        print('[*] Data received: {}'.format(data.decode('utf-8')))

                    connection.send(dashes.encode('utf-8') + data)

                    
def client():
    def setup_connection(message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
            client_tcp.connect((client_host, port))
            client_tcp.send(message.encode('utf-8'))
            data = client_tcp.recv(BUFFER_SIZE)
            yield print(f'The message was received from the server: {data.decode("utf-8")}')

    while True:
        message = input('enter a message or q for quit: ')
        if message == 'q':
            quit()
            
        next(setup_connection(message))


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'server':
            server()
        elif sys.argv[1] == 'client':
            client()
        else:
            print(":(")
    else:
        print(":(")
    
