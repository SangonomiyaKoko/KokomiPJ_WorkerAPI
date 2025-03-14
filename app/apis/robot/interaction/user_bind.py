import json

from app.log import ExceptionLogger
from app.response import JSONResponse
from app.network import ProxyAPI
from app.middlewares import RedisConnection

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
    data: dict
):
    """写入用户的绑定数据"""
    try:
        path = '/api/v1/wows/bot/user/bind/'
        params = {}
        result = await ProxyAPI.post(path=path, params=params, data=data)
        return result
    except Exception as e:
        raise e