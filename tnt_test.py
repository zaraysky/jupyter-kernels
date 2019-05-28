import selectors
import socket

CHUNK_LENGTH = 1024

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 3312  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect_ex((HOST, PORT))
    _buffer = ''
    while True:
        try:
            data = s.recv(CHUNK_LENGTH)
            _buffer += data.decode()
            if len(data) > CHUNK_LENGTH:
                continue
            else:
                print("Received", str(_buffer))
                _buffer = ''
                command = input('Enter command or press Ctrl-C\n> ')
                s.sendall((command+'\n').encode())

        except KeyboardInterrupt:
            print('BYEBYE')
            break

    # s.sendall(b"Hello, world")
    # data = s.recv(1024)

    print("Received", str(_buffer))
    # print("Received1", repr(data), len(data))
    # if len(data) < 1024:
    #     s.send("help\n".encode('utf-8'))
    #     data = s.recv(1024)
    #     print("Received2", repr(data), len(data))
#
