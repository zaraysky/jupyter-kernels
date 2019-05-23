from ipykernel.kernelapp import IPKernelApp
from .echokernel import EchoKernel
IPKernelApp.launch_instance(kernel_class=EchoKernel)
