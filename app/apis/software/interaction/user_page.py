from app.log import ExceptionLogger
from app.network import DetailsAPI
from app.response import JSONResponse
from app.middlewares import RedisConnection
from app.utils import UtilityFunctions, TimeFormat

from .user_base import get_user_name_and_clan

from ..processors.user_page import (
    process_overall_data
)

@ExceptionLogger.handle_program_exception_async
async def user_page(
    account_id: int, 
    region_id: int
):
    try:
        # 返回数据的格式
        data = {
            'header': {
                'region': {},
                'user': {},
                'clan': {}
            },
            'PlayerDatas': {}, 
            'ships': {}
        }
        # 读取ac数据
        redis = RedisConnection.get_connection()
        cache1_key = f"token_cache_1:{region_id}:{account_id}"
        token_cache1 = await redis.get(cache1_key)
        ac_value = None
        if token_cache1:
            ac_value = token_cache1
        user_and_clan_result = await get_user_name_and_clan(
            account_id=account_id,
            region_id=region_id,
            ac_value=ac_value
        )
        if user_and_clan_result['code'] != 1000:
            return user_and_clan_result
        else:
            data['header']['region'] = {
                'id': str(region_id),
                'name': UtilityFunctions.get_region(region_id)
            }
            user_result = user_and_clan_result['data']['user']
            data['header']['user'] = {
                'id': str(user_result['id']),
                'name': str(user_result['name']),
                'level': user_result['level'],
                'karmas': user_result['karma'],
                'created_at': (TimeFormat.get_current_timestamp() - user_result['created_at']) // (24*60*60),
                'actived_at': (TimeFormat.get_current_timestamp() - user_result['actived_at']) // (24*60*60)
            }
            clan_result = user_and_clan_result['data']['clan']
            if clan_result['id'] != None:
                data['header']['clan'] = {
                    'id': str(clan_result['id']),
                    'tag': str(clan_result['tag']),
                    'league': clan_result['league']
                }
            else:
                data['header']['clan'] = {
                    'id': None,
                    'tag': None,
                    'league': 5
                }
        # 请求数据
        details_data = await DetailsAPI.get_user_detail(
            account_id=account_id,
            region_id=region_id,
            type_list=['pvp'],
            ac_value=ac_value
        )
        for response in details_data:
            if response['code'] != 1000:
                return response
        processed_data = process_overall_data(
            account_id = account_id, 
            region_id = region_id, 
            responses = details_data,
        )
        if processed_data.get('code', None) != 1000:
            return processed_data
        data['PlayerDatas'] = processed_data['data']
        # 返回结果
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e