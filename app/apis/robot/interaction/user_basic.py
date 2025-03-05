from app.log import ExceptionLogger
from app.network import DetailsAPI
from app.response import JSONResponse
from app.middlewares import RedisConnection

from .user_base import get_user_name_and_clan
from ..processors.user_basic import (
    process_signature_data,
    process_lifetime_data,
    process_overall_data,
    process_random_data,
    process_ranked_data
    
)

@ExceptionLogger.handle_program_exception_async
async def wws_user_basic(
    account_id: int, 
    region_id: int, 
    game_type: str,
    language: str,
    algo_type: str
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
        cache2_key = f"token_cache_2:{region_id}:{account_id}"
        token_cache2 = await redis.get(cache2_key)
        ac2_value = None
        if token_cache2:
            ac2_value = token_cache2
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
        # 获取需要请求的数据和处理数据函数的引用
        game_type_dict = {
            'signature': {
                'type_list': ['pvp','rank_solo'],
                'func_reference': process_signature_data
            },
            'lifetime': {
                'type_list': ['pvp','lifetime'],
                'func_reference': process_lifetime_data
            },
            'overall': {
                'type_list': ['pvp_solo','pvp_div2','pvp_div3','rank_solo'],
                'func_reference': process_overall_data
            },
            'random': {
                'type_list': ['pvp_solo','pvp_div2','pvp_div3'],
                'func_reference': process_random_data
            },
            'ranked': {
                'type_list': ['rank_solo'],
                'func_reference': process_ranked_data
            },
            'operation': {
                'type_list': ['oper'],
                'func_reference': None
            },
            'clan_battle': {
                'type_list': ['clan','achievement'],
                'func_reference': None
            }
        }
        game_type_data = game_type_dict.get(game_type)
        # 请求数据
        details_data = await DetailsAPI.get_user_detail(
            account_id=account_id,
            region_id=region_id,
            type_list=game_type_data.get('type_list'),
            ac_value=ac_value,
            ac2_value=ac2_value
        )
        for response in details_data:
            if response['code'] != 1000:
                return response
        if game_type == 'ranked':
            details_data.append(user_and_clan_result['rank'])
        # 处理数据
        handle_api_data_func: function = game_type_data.get('func_reference')
        if not handle_api_data_func:
            raise NotImplementedError
        processed_data = handle_api_data_func(
            account_id = account_id, 
            region_id = region_id, 
            responses = details_data,
            language = language,
            algo_type = algo_type
        )
        if processed_data.get('code', None) != 1000:
            return processed_data
        data['statistics'] = processed_data['data']
        # 返回结果
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e