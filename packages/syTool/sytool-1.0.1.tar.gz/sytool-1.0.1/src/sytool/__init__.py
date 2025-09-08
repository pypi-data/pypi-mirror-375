"""
Sawyer Tools
======================
工具包集

:copyright: (c) 2025 by laishaoya.
:license: GPLv3 for non-commercial project, see README for more details.
"""

__version__ = "1.0.0"
__author__ = "Sawyerlsy"


def show_banner():
    """显示艺术字标识"""
    banner = r"""
    ███████╗██╗   ██╗████████╗ ██████╗  ██████╗ ██╗     
    ██╔════╝╚██╗ ██╔╝╚══██╔══╝██╔═══██╗██╔═══██╗██║     
    ███████╗ ╚████╔╝    ██║   ██║   ██║██║   ██║██║     
    ╚════██║  ╚██╔╝     ██║   ██║   ██║██║   ██║██║     
    ███████║   ██║      ██║   ╚██████╔╝╚██████╔╝███████╗
    ╚══════╝   ╚═╝      ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    """
    print(banner)
    print(f"📢 Version: {__version__} | Author: {__author__}")
show_banner()

from .cache import *
from .common import *
from .db import *
from .file import *
from .http import *
from .time import *
from .thread import *
