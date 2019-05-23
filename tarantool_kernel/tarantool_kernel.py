from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF
import pexpect

from subprocess import check_output
import os.path

import re
import signal

__version__ = '0.1'

version_pat = re.compile(r'Tarantool (\d+\.\d+\.\d+\-\d+\-.{8})')

from .images import (
    extract_image_filenames, display_data_for_image, image_setup_cmd
)

class IREPLWrapper(replwrap.REPLWrapper):
    """A subclass of REPLWrapper that gives incremental output
    specifically for bash_kernel.

    The parameters are the same as for REPLWrapper, except for one
    extra parameter:

    :param line_output_callback: a callback method to receive each batch
      of incremental output. It takes one string parameter.
    """
    # def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
    #              extra_init_cmd=None, line_output_callback=None):
    #     self.line_output_callback = line_output_callback
    #     replwrap.REPLWrapper.__init__(self, cmd_or_spawn, orig_prompt,
    #                                   prompt_change, extra_init_cmd=extra_init_cmd)
    #
    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 extra_init_cmd=None, line_output_callback=None, new_prompt=None,
                                                  continuation_prompt=None):
        self.line_output_callback = line_output_callback
        replwrap.REPLWrapper.__init__(self, cmd_or_spawn, orig_prompt,
                                      prompt_change, extra_init_cmd=extra_init_cmd,
                                      new_prompt=new_prompt,
                                      continuation_prompt=continuation_prompt
                                      )


class TarantoolKernel(Kernel):
    implementation = 'tarantool_kernel'
    implementation_version = __version__

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['tarantool', '--version']).decode('utf-8')
        return self._banner

    language_info = {'name': 'lua',
                     'codemirror_mode': 'shell',
                     'mimetype': 'text/x-lua',
                     'file_extension': '.lua'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_tarantool()

    def _start_tarantool(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that bash and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            # Note: the next few lines mirror functionality in the
            # bash() function of pexpect/replwrap.py.  Look at the
            # source code there for comments and context for
            # understanding the code here.
            child = pexpect.spawn("tarantool", [], echo=False,
                                  encoding='utf-8', codec_errors='replace')

            # Using IREPLWrapper to get incremental output
            # self.tarantool_wrapper = IREPLWrapper(child, 'tarantool>', prompt_change='None',
            #                                       extra_init_cmd="",
            #                                       line_output_callback=self.process_output)
            # self.tarantool_wrapper = IREPLWrapper(cmd_or_spawn="tarantool",
            #                                       orig_prompt="tarantool> ",
            #                                       prompt_change='None',
            #                                       new_prompt='',
            #                                       continuation_prompt='tarantool>')

            self.tarantool_wrapper = IREPLWrapper(child,
                                                  orig_prompt="tarantool> ",
                                                  prompt_change='None',
                                                  new_prompt='',
                                                  continuation_prompt='tarantool>')


        finally:
            signal.signal(signal.SIGINT, sig)

        # Register Bash function to write image data to temporary file
        self.tarantool_wrapper.run_command(image_setup_cmd)

    def process_output(self, output):
        if not self.silent:
            # image_filenames, output = extract_image_filenames(output)

            # Send standard output
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

            # Send images, if any
            # for filename in image_filenames:
            #     try:
            #         data = display_data_for_image(filename)
            #     except ValueError as e:
            #         message = {'name': 'stdout', 'text': str(e)}
            #         self.send_response(self.iopub_socket, 'stream', message)
            #     else:
            #         self.send_response(self.iopub_socket, 'display_data', data)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        self.silent = silent
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted = False
        try:
            # Note: timeout=None tells IREPLWrapper to do incremental
            # output.  Also note that the return value from
            # run_command is not needed, because the output was
            # already sent by IREPLWrapper.
            self.tarantool_wrapper.run_command(code.rstrip(), timeout=-1)
        except KeyboardInterrupt:
            self.tarantool_wrapper.child.sendintr()
            interrupted = True
            self.tarantool_wrapper._expect_prompt()
            output = self.tarantool_wrapper.child.before
            self.process_output(output)
        except EOF:
            output = self.tarantool_wrapper.child.before + 'Restarting Tarantool'
            self._start_tarantool()
            self.process_output(output)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

    def do_complete(self, code, cursor_pos):
        # code = code[:cursor_pos]
        default = {'matches': [], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}
        return default


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=TarantoolKernel)