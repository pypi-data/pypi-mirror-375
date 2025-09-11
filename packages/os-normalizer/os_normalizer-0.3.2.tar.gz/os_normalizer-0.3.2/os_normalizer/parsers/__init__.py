from .windows import parse_windows
from .macos import parse_macos
from .linux import parse_linux
from .mobile import parse_mobile
from .bsd import parse_bsd
from .network import parse_network

__all__ = [
    "parse_windows",
    "parse_macos",
    "parse_linux",
    "parse_mobile",
    "parse_bsd",
    "parse_network",
]

