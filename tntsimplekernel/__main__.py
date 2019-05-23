from ipykernel.kernelapp import IPKernelApp
from .tntsimplekernel import TNTSimpleKernel
IPKernelApp.launch_instance(kernel_class=TNTSimpleKernel)
