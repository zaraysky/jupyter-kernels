import tarantool
import json
import socket
from ipykernel.kernelbase import Kernel

from .config import CHUNK_LENGTH, HOST, PORT, START_OF_RESPONSE, START_OF_STRING, END_OF_RESPONSE
from .utils import TNTCodeParser


def parse_response(response: str) -> str:
    if "type 'help' for interactive help" in response:
        return ''  # response
    response_strings = response.split('\n')
    if response_strings[0] == START_OF_RESPONSE and \
            response_strings[-2] == END_OF_RESPONSE:
        return '\n'.join(response_strings[1:-2]) if len(response_strings) > 3 else 'OK'
    else:
        return f'Some error in response: {response}'


def send_receive(s: socket, cmd: str, tab=False) -> str:
    if tab:
        cmd = '_G.' + chr(9)
        s.sendall(cmd.encode())
        _buffer = ''
        while True:
            data = s.recv(CHUNK_LENGTH)
            _buffer += data.decode()
            if len(data) > CHUNK_LENGTH:
                continue
            else:
                return _buffer
    else:
        s.sendall((cmd + (cmd[-2:] == '\n' and '' or '\n')).encode())
        _buffer = ''
        while True:
            data = s.recv(CHUNK_LENGTH)
            _buffer += data.decode()
            if len(data) > CHUNK_LENGTH:
                continue
            else:
                return parse_response(_buffer)

class TNTSimpleKernel(Kernel):

    implementation = 'TNTSocket'
    implementation_version = '0.2'
    language = 'lua'
    language_version = '0.1'
    language_info = {'name': 'lua',
                     'codemirror_mode': 'shell',
                     'mimetype': 'text/x-lua',
                     'file_extension': '.lua'}

    banner = "TNT Simple kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = TNTCodeParser
        self.tnt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tnt_socket.connect_ex((HOST, PORT))

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if silent:  # I don't know WTF is silent
            parsed_code = code
            stream_content = {'name': 'stdout', 'text': parsed_code}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        else:
            response = send_receive(self.tnt_socket, code)

            stream_content = {'name': 'stdout', 'text': response}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    def do_complete(self, code, cursor_pos):
        # code = code[:cursor_pos]
        response = send_receive(self.tnt_socket, code, tab=True)

        matches = response.split(chr(9))
        default = {'matches': matches, 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}
        return default


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=TNTSimpleKernel)
