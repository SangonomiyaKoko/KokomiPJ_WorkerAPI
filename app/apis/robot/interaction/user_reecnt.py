from app.log import ExceptionLogger
from app.network import DetailsAPI
from app.response import JSONResponse
from app.middlewares import RedisConnection

from .user_base import get_user_name_and_clan

@ExceptionLogger.handle_program_exception_async
async def wws_user_recent(
    account_id: int, 
    region_id: int, 
    game_type: str,
    language: str,
    algo_type: str,
    start_date: str,
    end_date: str,
    ship_id: int
):
    '''用于`wws me`功能的接口

    返回用户基本数据
    
    参数:
        account_id 用户id
        region_id 服务器id
        game_type 数据类型
        algo_type 算法类型

    返回:
        ResponseDict
    '''
    try:
        # 返回数据的格式
        data = {
            'user': {},
            'clan': {}, 
            'statistics': {}
        }
        # 读取ac数据
        redis = RedisConnection.get_connection()
        cache1_key = f"token_cache_1:{region_id}:{account_id}"
        token_cache1 = await redis.get(cache1_key)
        ac_value = None
        if token_cache1:
            ac_value = token_cache1
        # 获取用户user和clan数据
        if game_type == 'ranked':
            user_and_clan_result = await get_user_name_and_clan(
                account_id=account_id,
                region_id=region_id,
                ac_value=ac_value,
                rank_data=True
            )
        else:
            user_and_clan_result = await get_user_name_and_clan(
                account_id=account_id,
                region_id=region_id,
                ac_value=ac_value
            )
        if user_and_clan_result['code'] != 1000:
            return user_and_clan_result
        else:
            data['user'] = user_and_clan_result['data']['user']
            data['clan'] = user_and_clan_result['data']['clan']

        
        # 返回结果
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e