"""
hikvision_isapi_utils

一个用于与海康威视 (Hikvision) ISAPI 设备进行通信的工具库。
提供同步和异步的 HTTP 客户端。
"""

from .client import Client
from .asyncclient import AsyncClient

__all__ = [
    "Client",
    "AsyncClient",
]

# 可选：定义库的版本号
__version__ = "0.1.0"