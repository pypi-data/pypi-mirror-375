# 标准库
import logging
from urllib.parse import urljoin
from typing import Optional, Any
# 第三方库
import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import RequestException, Timeout, ConnectionError

# 为当前模块创建一个 logger 实例
logger = logging.getLogger(__name__)

class Client:
    """
    一个用于与支持 ISAPI 的设备进行通信的 HTTP 客户端。
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
        初始化客户端实例。

        Args:
            ip (str): 设备的 IP 地址。
            username (str): 用于认证的用户名。
            password (str): 用于认证的密码。
            port (Optional[int]): 设备端口。如果为 None，则根据协议默认为 80 (http) 或 443 (https)。
            protocol (str): 通信协议，'http' 或 'https'。默认为 'http'。
            **kwargs: 传递给 `requests.Session` 的额外参数，例如 `headers`, `proxies`。
        """
        self.protocol = protocol.lower()
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port if port is not None else (443 if self.protocol == 'https' else 80)
        self.base_url = f"{self.protocol}://{self.ip}:{self.port}"
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(username, password)
        # 默认不验证 SSL 证书，适用于自签名证书环境
        self.session.verify = False
        # 应用传入的额外参数到 session
        for key, value in kwargs.items():
            if hasattr(self.session, key):
                setattr(self.session, key, value)

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        """
        向指定端点发送 HTTP 请求。
        该方法会自动处理因会话过期导致的 401 认证失败，并尝试使用原始凭据重新认证一次。

        Args:
            method (str): HTTP 请求方法 (e.g., 'GET', 'POST', 'PUT', 'DELETE')。
            endpoint (str): API 端点路径。
            **kwargs: 传递给 `requests.Session.request` 的额外参数，例如 `timeout`, `json`, `data`。

        Returns:
            requests.Response: HTTP 响应对象。

        Raises:
            requests.exceptions.Timeout: 请求超时。
            requests.exceptions.ConnectionError: 网络连接错误。
            requests.exceptions.RequestException: 其他请求相关的异常。
            # 注意: 对于 4xx/5xx HTTP 状态码，此方法不会主动抛出异常，
            #       调用者需检查 response.status_code 或调用 response.raise_for_status()。
        """
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.request(method, url, **kwargs)
            # 处理 401 未授权响应
            if response.status_code == 401:
                logger.info(f"收到 401 响应，端点: {endpoint}。尝试刷新认证信息。")
                # 刷新认证信息
                self.session.auth = HTTPDigestAuth(self.username, self.password)
                # 重试请求
                response = self.session.request(method, url, **kwargs)
                if response.status_code == 401:
                    logger.warning(f"刷新认证后仍收到 401 响应，端点: {endpoint}。请检查用户名和密码。")
            return response
        except Timeout as e:
            logger.warning(f"请求超时，端点: {endpoint}。")
            raise e
        except ConnectionError as e:
            logger.warning(f"连接错误，端点: {endpoint}。")
            raise e
        except RequestException as e:
            logger.info(f"请求发生异常，端点: {endpoint}，异常: {e}")
            raise e

    def close(self):
        """
        关闭客户端会话，释放资源。
        建议在不再需要客户端时显式调用此方法。
        """
        self.session.close()

    def __enter__(self):
        """进入上下文管理器。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器，关闭会话。"""
        self.session.close()
        # 不抑制异常，异常将继续传播
        return False
    