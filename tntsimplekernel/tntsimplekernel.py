from ipykernel.kernelbase import Kernel
import tarantool
import json

from tarantool.error import DatabaseError

class TNTSimpleKernel(Kernel):

    implementation = 'TNTSimple'
    implementation_version = '0.1'
    language = 'no-op'
    language_version = '0.1'
    language_info = {'name': 'lua',
                     'codemirror_mode': 'shell',
                     'mimetype': 'text/x-lua',
                     'file_extension': '.lua'}

    banner = "TNT Simple kernel"

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):

        if not silent:
            connection = tarantool.connect(
                host='localhost',
                port=3300,
                user='guest')
            connection.connect()

            response = connection.eval(f"""
            local f = loadstring([[{code}]])
            local status, err = pcall(f)

            return status, err""")

            connection.close()

            success, result = response._data

            if isinstance(result, dict):
                output = json.dumps(response._data[1], indent=4, sort_keys=True)
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
