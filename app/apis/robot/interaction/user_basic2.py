from app.log import ExceptionLogger
from app.network import DetailsAPI
from app.response import JSONResponse
from app.middlewares import RedisConnection

from .user_base import get_user_name_and_clan
from ..processors.user_basic import process_overall_data

@ExceptionLogger.handle_program_exception_async
async def wws_user_basic(
    account_id: int, 
    region_id: int, 
    language: str,
    algo_type: str,
    filter_type: str = None
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
        # 获取需要请求的数据和处理数据函数的引用
        # 请求数据
        details_data = await DetailsAPI.get_user_detail(
            account_id=account_id,
            region_id=region_id,
            type_list=['pvp_solo','pvp_div2','pvp_div3','rank_solo'],
            ac_value=ac_value
        )
        for response in details_data:
            if response['code'] != 1000:
                return response
        # 处理数据
        processed_data = process_overall_data(
            account_id = account_id, 
            region_id = region_id, 
            responses = details_data,
            language = language,
            algo_type = algo_type,
            filter_type = filter_type
        )
        if processed_data.get('code', None) != 1000:
            return processed_data
        data['statistics'] = processed_data['data']
        # 返回结果
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e