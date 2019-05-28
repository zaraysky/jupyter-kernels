import socket
HOST = '127.0.0.1'
PORT = 3312

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # s.setblocking(0)
    try:
        data = s.recv(128)
    except socket.error:
        print('No data')
    else:
    # if data:
        print('received', repr(data), len(data))

    s.sendall(b'a=1')
    try:
        data = s.recv(128)
    except socket.error:
        print('No data')
    else:
    # if data:
        print('received', repr(data), len(data))
