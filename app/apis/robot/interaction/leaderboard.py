import json

from app.log import ExceptionLogger
from app.response import JSONResponse
from app.network import ProxyAPI
from app.middlewares import RedisConnection
from app.utils import ShipName, TimeFormat

from .user_base import get_user_name_and_clan
from ..processors.leaderboard import (
    process_leaderboard_page_data, 
    process_leaderboard_overall_data,
    process_leaderboard_rank_data
)

@ExceptionLogger.handle_program_exception_async
async def get_leaderboard_page(
    region_idx: int,
    ship_id: int,
    page_idx: int,
    page_size: int,
    language: str
):
    """获取用户的绑定数据

    从缓存读取
    """
    try:
        result = {
            'ship_data': {
                'region': None,
                'limit': None,
                'update': None
            },
            'ship_info': None,
            'leaderboard': []
        }
        # 区分global和single
        limit_tier_dict = {
            6: '40',
            7: '40',
            8: '40',
            9: '50',
            10: '60',
            11: '60'
        }
        if region_idx:
            ship_data = ShipName.get_ship_info_batch(region_idx, language, [ship_id])
            if ship_id not in ship_data:
                return JSONResponse.API_1000_Success
            else:
                result['ship_info'] = ship_data[ship_id]
        else:
            ship_data_1 = ShipName.get_ship_info_batch(1, language, [ship_id])
            ship_data_4 = ShipName.get_ship_info_batch(4, language, [ship_id])
            if ship_id in ship_data_1:
                result['ship_info'] = ship_data_1[ship_id]
            elif ship_id in ship_data_4:
                result['ship_info'] = ship_data_4[ship_id]
            else:
                return JSONResponse.API_1000_Success
        if result['ship_info']['tier'] not in limit_tier_dict:
            return JSONResponse.API_1000_Success
        redis = RedisConnection.get_connection()
        key = f"leaderboard:{region_idx}:{ship_id}:{page_idx}"
        data = await redis.get(key)
        page_data = None
        if data:
            page_data = json.loads(data)
        else:
            path = f'/api/v1/wows/leaderboard/page/{region_idx}/{ship_id}/'
            params = {'page': page_idx, 'page_size': page_size}
            page_data = await ProxyAPI.get(path=path, params=params)
            if page_data['code'] != 1000:
                return page_data
            if page_data['data'] == None or page_data['data'] == {}:
                return JSONResponse.API_1000_Success
            page_data = page_data['data']
        region_id_dict = {
            0: 'Global',
            1: 'Asia',
            2: 'Eu',
            3: 'Na',
            4: 'Ru',
            5: 'Cn'
        }
        result['ship_data']['limit'] = limit_tier_dict.get(result['ship_info']['tier'])
        result['ship_data']['region'] = region_id_dict.get(region_idx)
        now_time = TimeFormat.get_current_timestamp()
        last_update = int(now_time - page_data['update_time']) // 60
        result['ship_data']['update'] = f"{last_update}m"
        result['leaderboard'] = process_leaderboard_page_data(page_data['page_data'])

        return JSONResponse.get_success_response(result)
    except Exception as e:
        raise e
    
@ExceptionLogger.handle_program_exception_async
async def get_user_leaderboard_data(
    region_idx: int,
    ship_id: int,
    region_id: int,
    account_id: int,
    language: str
):
    try:
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
        result = {
            'overall': {},
            'ship_data': {
                'region': None,
                'limit': None,
                'update': None
            },
            'ship_info': None,
            'rank_data': None,
            'leaderboard': []
        }
        limit_tier_dict = {
            6: '40',
            7: '40',
            8: '40',
            9: '50',
            10: '60',
            11: '60'
        }
        if region_idx:
            ship_data = ShipName.get_ship_info_batch(region_idx, language, [ship_id])
            if ship_id not in ship_data:
                return JSONResponse.API_1000_Success
            else:
                result['ship_info'] = ship_data[ship_id]
        else:
            ship_data_1 = ShipName.get_ship_info_batch(1, language, [ship_id])
            ship_data_4 = ShipName.get_ship_info_batch(4, language, [ship_id])
            if ship_id in ship_data_1:
                result['ship_info'] = ship_data_1[ship_id]
            elif ship_id in ship_data_4:
                result['ship_info'] = ship_data_4[ship_id]
            else:
                return JSONResponse.API_1000_Success
        if result['ship_info']['tier'] not in limit_tier_dict:
            return JSONResponse.API_1000_Success
        
        path = f'/api/v1/wows/leaderboard/user/{region_idx}/{ship_id}/{account_id}/'
        params = {}
        page_data = await ProxyAPI.get(path=path, params=params)
        if page_data['code'] != 1000:
            return page_data
        if page_data['data'] == None or page_data['data'] == {}:
            return JSONResponse.API_1000_Success
        region_id_dict = {
            0: 'Global',
            1: 'Asia',
            2: 'Eu',
            3: 'Na',
            4: 'Ru',
            5: 'Cn'
        }
        result['ship_data']['limit'] = limit_tier_dict.get(result['ship_info']['tier'])
        result['ship_data']['region'] = region_id_dict.get(region_idx)
        now_time = TimeFormat.get_current_timestamp()
        last_update = int(now_time - page_data['data']['update_time']) // 60
        result['ship_data']['update'] = f"{last_update}m"

        result['overall'] = process_leaderboard_overall_data(page_data['data']['user_data'])
        result['rank_data'] = process_leaderboard_rank_data(page_data['data']['rank_data'])
        result['leaderboard'] = process_leaderboard_page_data(page_data['data']['page_data'])

        data['statistics'] = result
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e
    
@ExceptionLogger.handle_program_exception_async
async def update_user_cache(
    region_id: int,
    account_id: int
):
    """更新用户的缓存数据
    """
    try:
        path = f'/api/v1/wows/leaderboard/update/{region_id}/{account_id}/'
        params = {}
        result = await ProxyAPI.get(path=path, params=params)
        return result
    except Exception as e:
        raise e