import json

from app.network import BasicAPI
from app.log import ExceptionLogger
from app.response import JSONResponse
from app.network import ProxyAPI
from app.middlewares import RedisConnection

from ..processors.check import process_check_user_data

@ExceptionLogger.handle_program_exception_async
async def get_user_bind(
    platform: str,
    user_id: str
):
    """获取用户的绑定数据

    从缓存读取
    """
    try:
        redis = RedisConnection.get_connection()
        key = f"app_bot:bind_cache:{platform}:{user_id}"
        data = await redis.get(key)
        if data:
            data = json.loads(data)
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e
    
@ExceptionLogger.handle_program_exception_async
async def post_user_bind(
    user_data: dict
):
    """写入用户的绑定数据"""
    try:
        data = {
            'user': {},
            'func': {}
        }
        region_id = user_data['region_id']
        account_id = user_data['account_id']
        basic_data = {
            'id': account_id,
            'region': region_id,
            'name': None,
            'hidden': None
        }
        func_data = {
            'recent': False,
            'recents': False
        }
        result = await BasicAPI.get_user_basic(account_id, region_id)
        if result[0]['code'] != 1000:
            return result[0]
        result = process_check_user_data(region_id,account_id,result[0])
        basic_data['name'] = result['data']['name']
        basic_data['hidden'] = result['data']['hidden']
        data['user'] = basic_data
        path = '/api/v1/wows/bot/user/bind/'
        params = {}
        result = await ProxyAPI.post(path=path, params=params, data=user_data)
        if result['code'] != 1000:
            return result
        if result['data']['recent']:
            func_data['recent'] = True
        if result['data']['recents']:
            func_data['recents'] = True
        data['func'] = func_data
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e