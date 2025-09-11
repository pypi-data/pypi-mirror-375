import platform

if "linux" in platform.platform() or "Linux" in platform.platform():
    from .launch import *
    from .mpiRun import *
    from .common import *
    from .util import *