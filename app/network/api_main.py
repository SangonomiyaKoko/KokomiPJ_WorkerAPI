import httpx

from .api_base import BaseUrl
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.core import EnvConfig
from app.utils import UtilityFunctions

config = EnvConfig.get_config()

class MainAPI:
    '''其他接口
    '''
    @ExceptionLogger.handle_network_exception_async
    async def fetch_data(url):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url=url, timeout=BaseUrl.REQUEST_TIME_OUT)
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    # 正常返回值的处理
                    return requset_result
                else:
                    res.raise_for_status()  # 其他状态码
        except Exception as e:
            raise e
        
    @classmethod
    async def get_user_basic(cls, account_id: int, region_id: int) -> ResponseDict:
        main_api_url = f"http://{config.MAIN_SERVICE_HOST}:8000"
        path = '/r/user/account/'
        region = UtilityFunctions.get_region(region_id)
        url = main_api_url + path + f"?region={region}&account_id={account_id}"
        result = await cls.fetch_data(url)
        return result
    
    @classmethod
    async def get_clan_basic(cls, clan_id: int, region_id: int) -> ResponseDict:
        main_api_url = f"http://{config.MAIN_SERVICE_HOST}:8000"
        path = '/r/path/clan/'
        region = UtilityFunctions.get_region(region_id)
        url = main_api_url + path + f"?region={region}&clan_id={clan_id}"
        result = await cls.fetch_data(url)
        return result
        