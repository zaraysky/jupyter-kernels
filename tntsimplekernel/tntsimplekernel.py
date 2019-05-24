from ipykernel.kernelbase import Kernel
import tarantool
import json

from .utils import TNTCodeParser


class TNTSimpleKernel(Kernel):

    implementation = 'TNTSimple'
    implementation_version = '0.1'
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

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):

        if silent:
        # if not silent:

            parsed_code = self.parser.parse(code)
            stream_content = {'name': 'stdout', 'text': parsed_code}
            self.send_response(self.iopub_socket, 'stream', stream_content)

            pass
        else:
            connection = tarantool.connect(
                host='localhost',
                port=3300,
                user='guest')
            connection.connect()

            parsed_code = self.parser.parse(code)

            response = connection.eval(f"""
            local f = loadstring([[{parsed_code}]])
            local status, err = pcall(f)

            return status, err""")

            connection.close()

            success, result = response._data

            if isinstance(result, dict):
                output = json.dumps(response._data[1], indent=4, sort_keys=True)
            elif isinstance(result, list):

                s = [[str(e) for e in row] for row in result]
                lens = [max(map(len, col)) for col in zip(*s)]
                fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
                table = [fmt.format(*row) for row in s]

                output = '\n'.join(table)
            else:
                if result is None:
                    output = 'OK'
                    # output = f'{type(result)} : {result}' if success else f'Error: {result}'
                else:
                    output = f'{type(result)} : {result}' if success else f'Error: {result}'

            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    def do_complete(self, code, cursor_pos):
        # code = code[:cursor_pos]
        default = {'matches': ['foo', 'bar', 'foobar'], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}
        return default


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=TNTSimpleKernel)
