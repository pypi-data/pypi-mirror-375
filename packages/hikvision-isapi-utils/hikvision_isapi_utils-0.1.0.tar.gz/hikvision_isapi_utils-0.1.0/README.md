# hikvision-isapi-utils

一个用于与海康威视 (Hikvision) 设备进行通信的 Python 库，支持同步和异步操作。

## 安装

```bash
pip install hikvision-isapi-utils
```

## 快速开始

### 同步客户端

```python
from hikvision_isapi_utils import Client

# 创建客户端
client = Client(
    ip="192.168.1.64",
    username="admin",
    password="your_password",
    protocol="http"
)

# 发送请求
response = client._request("GET", "/ISAPI/System/deviceInfo")
print(response.text)

# 关闭客户端
client.close()
```

### 异步客户端

```python
import asyncio
from hikvision_isapi_utils import AsyncClient

async def main():
    async with AsyncClient(
        ip="192.168.1.64",
        username="admin",
        password="your_password",
        protocol="http"
    ) as client:
        response = await client._request("GET", "/ISAPI/System/deviceInfo")
        print(response.text)

# 运行异步函数
asyncio.run(main())
```

## 依赖

*   Python >= 3.8
*   `requests`
*   `httpx`

## 许可证

本项目采用 MIT 许可证。详情请见 `LICENSE` 文件。