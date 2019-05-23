from ipykernel.kernelapp import IPKernelApp
from .tarantool_kernel import TarantoolKernel
IPKernelApp.launch_instance(kernel_class=TarantoolKernel)
