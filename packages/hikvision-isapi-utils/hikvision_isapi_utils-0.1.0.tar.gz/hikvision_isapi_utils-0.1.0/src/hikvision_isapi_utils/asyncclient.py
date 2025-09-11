# 标准库
import logging
from urllib.parse import urljoin
from typing import Optional, Any
import asyncio
# 第三方库
import httpx
from httpx import DigestAuth
from httpx import AsyncClient as HttpxAsyncClient, TimeoutException, ConnectError, RequestError

# 为当前模块创建一个 logger 实例
logger = logging.getLogger(__name__)

class AsyncClient:
    """
    一个用于与支持 ISAPI 的设备进行异步通信的 HTTP 客户端。
    支持 Digest 认证和会话管理。
    """

    def __init__(
        self,
        ip: str,
        username: str,
        password: str,
        port: Optional[int] = None,
        protocol: str = 'http',
        **kwargs
    ):
        """
        初始化异步客户端实例。

        Args:
            ip (str): 设备的 IP 地址。
            username (str): 用于认证的用户名。
            password (str): 用于认证的密码。
            port (Optional[int]): 设备端口。如果为 None，则根据协议默认为 80 (http) 或 443 (https)。
            protocol (str): 通信协议，'http' 或 'https'。默认为 'http'。
            **kwargs: 传递给 `httpx.AsyncClient` 的额外参数，例如 `headers`, `proxies`, `timeout`。
        """
        self.protocol = protocol.lower()
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port if port is not None else (443 if self.protocol == 'https' else 80)
        self.base_url = f"{self.protocol}://{self.ip}:{self.port}"
        # 创建 AsyncClient 实例 [[2]]
        self.auth = DigestAuth(username, password)
        # 默认不验证 SSL 证书
        kwargs.setdefault('verify', False)
        # 应用传入的额外参数到 AsyncClient
        self.client_kwargs = kwargs
        self._client = None  # 延迟初始化

    @property
    def client(self) -> HttpxAsyncClient:
        """获取或创建异步客户端实例。"""
        if self._client is None:
            self._client = HttpxAsyncClient(auth=self.auth, **self.client_kwargs)
        return self._client

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        """
        向指定端点异步发送 HTTP 请求。
        该方法会自动处理因会话过期导致的 401 认证失败，并尝试使用原始凭据重新认证一次。

        Args:
            method (str): HTTP 请求方法 (e.g., 'GET', 'POST', 'PUT', 'DELETE')。
            endpoint (str): API 端点路径。
            **kwargs: 传递给 `httpx.AsyncClient.request` 的额外参数，例如 `timeout`, `json`, `data`。

        Returns:
            httpx.Response: HTTP 响应对象。

        Raises:
            httpx.TimeoutException: 请求超时.
            httpx.ConnectError: 网络连接错误.
            httpx.RequestError: 其他请求相关的异常.
        """
        url = urljoin(self.base_url, endpoint)
        try:
            response = await self.client.request(method, url, **kwargs)
            # 处理 401 未授权响应
            if response.status_code == 401:
                logger.info(f"收到 401 响应，端点: {endpoint}。尝试刷新认证信息。")
                # 直接更新客户端的 auth 属性，而不是重建整个客户端
                self.client.auth = DigestAuth(self.username, self.password) # 更新为新的 DigestAuth 实例
                # 重试请求
                response = await self.client.request(method, url, **kwargs)
                if response.status_code == 401:
                    logger.warning(f"刷新认证后仍收到 401 响应，端点: {endpoint}。请检查用户名和密码。")
            return response
        except TimeoutException as e:
            logger.warning(f"请求超时，端点: {endpoint}。")
            raise e
        except ConnectError as e:
            logger.warning(f"连接错误，端点: {endpoint}。")
            raise e
        except RequestError as e:
            logger.info(f"请求发生异常，端点: {endpoint}，异常: {e}")
            raise e

    async def close(self):
        """
        关闭异步客户端会话，释放资源。
        建议在不再需要客户端时显式调用此方法。
        """
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """进入异步上下文管理器。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出异步上下文管理器，关闭会话。"""
        await self.close()
        # 不抑制异常，异常将继续传播
        return False
