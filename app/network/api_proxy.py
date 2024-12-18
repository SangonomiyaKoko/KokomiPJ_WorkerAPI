import httpx

from .api_base import BaseUrl
from app.log import ExceptionLogger
from app.core import EnvConfig

config = EnvConfig.get_config()

class ProxyAPI:
    @ExceptionLogger.handle_network_exception_async
    async def get(path, params: dict):
        try:
            base_url = f"http://{config.MAIN_SERVICE_HOST}:8000" + path
            if params == {}:
                url = '{}'.format(base_url)
            else:
                url = '{}?{}'.format(base_url, '&'.join(['{}={}'.format(key, value) for key, value in params.items()]))
            async with httpx.AsyncClient() as client:
                res = await client.get(url=url, timeout=BaseUrl.PROXY_TIME_OUT)
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    # 正常返回值的处理
                    return requset_result
                else:
                    res.raise_for_status()  # 其他状态码
        except Exception as e:
            raise e

    @ExceptionLogger.handle_network_exception_async
    async def post(path, params: dict, data: dict):
        try:
            base_url = f"http://{config.MAIN_SERVICE_HOST}:8000" + path
            if params == {}:
                url = '{}'.format(base_url)
            else:
                url = '{}?{}'.format(base_url, '&'.join(['{}={}'.format(key, value) for key, value in params.items()]))
            async with httpx.AsyncClient() as client:
                res = await client.post(url=url, json=data, timeout=BaseUrl.PROXY_TIME_OUT)
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    # 正常返回值的处理
                    return requset_result
                else:
                    res.raise_for_status()  # 其他状态码
        except Exception as e:
            raise e