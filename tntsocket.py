import selectors
import socket

CHUNK_LENGTH = 1024

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 3312  # The port used by the server

START_OF_RESPONSE = '---'
START_OF_STRING = ' -'
END_OF_RESPONSE = '...'


def parse_response(response: str) -> str:
    if "type 'help' for interactive help" in response:
        return ''    # response
    response_strings = response.split('\n')
    if response_strings[0] == START_OF_RESPONSE and \
       response_strings[-2] == END_OF_RESPONSE:

        return '\n'.join(response_strings[1:-2]) if len(response_strings) > 3 else 'OK'
    else:
        return f'Some error in response: {response}'


def send_receive(s: socket, cmd: str) -> str:

    s.sendall((cmd + (cmd[-2:] == '\n' and '' or '\n')).encode())
    _buffer = ''
    while True:
        data = s.recv(CHUNK_LENGTH)
        _buffer += data.decode()
        if len(data) > CHUNK_LENGTH:
            continue
        else:
            return parse_response(_buffer)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tnt_socket:
    tnt_socket.connect_ex((HOST, PORT))

    print(send_receive(tnt_socket, ''))
    while True:
        try:
            command = input('Enter command or press Ctrl-C\n> ')
            print(send_receive(tnt_socket, command))

        except KeyboardInterrupt:
            print('\nBYEBYE')
            break
