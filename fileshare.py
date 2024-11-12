import socket
import sys
import threading

# client_host = '127.0.0.1'
server_host = '127.0.0.1'
port = 3300 # 3389

BUFFER_SIZE = 1024

# Server functions

def validate_command_server(message):
    def validate_cp():
        pass
    def validate_rm():
        pass
    def validate_ls():
        pass
    def validate_mkdir():
        pass
    pass


def send_nack(connection, error_message):
    pass


def send_ack(connection):
    pass


def execute_command_server(connection):
    def execute_cp():
        pass
    def execute_rm():
        pass
    def execute_ls():
        pass
    def execute_mkdir():
        pass
    pass


def server():
    thread_pool = []

    def server_thread(connection, addr):
        with connection:
            print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
            while True:
                command = connection.recv(BUFFER_SIZE)

                is_valid, error_message = validate_command_server(command)

                if is_valid:
                    send_ack(connection)
                    execute_command_server(connection)
                else:
                    send_nack(connection, error_message)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_tcp:
        server_tcp.bind((server_host, port))
        server_tcp.listen(6)
        print('[*] Waiting for connection')
        
        while True:
            connection, addr = server_tcp.accept()
            t = threading.Thread(target=server_thread, args=[connection, addr])
            t.start()
            thread_pool.append(t)


# Client functions

def validate_command_client(message):
    def validate_cp():
        pass
    def validate_rm():
        pass
    def validate_ls():
        pass
    def validate_mkdir():
        pass
    pass


def is_ack(message):
    pass


def is_nack(message):
    pass


def get_nack_message(message):
    pass


def execute_command_client(message, client_tcp):
    def execute_cp():
        pass
    def execute_rm():
        pass
    def execute_ls():
        pass
    def execute_mkdir():
        pass
    pass

                    
def client(ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((ip, port))
        while True:
            command = input('> ')
            if command == 'q':
                quit()

            is_valid, error_message = validate_command_client(command)
            if is_valid:
                client_tcp.send(command.encode('utf-8'))
                data = client_tcp.recv(BUFFER_SIZE)
                
                if is_ack(data):
                    execute_command_client(command, client_tcp)
                elif is_nack(data):
                    print('Error: ', get_nack_message(data))
                else:
                    print('huh?')
            else:
                print("Error: ", error_message)
            

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'server':
            server()
        elif sys.argv[1] == 'client':
            client(sys.argv[2])
        else:
            print(":(")
    else:
        print(":(")    
