from typing import Optional

from app.utils import UtilityFunctions
from app.network import BasicAPI, MainAPI
from app.response import JSONResponse, ResponseDict
from app.middlewares import celery_app

async def get_user_name_and_clan(
    account_id: int,
    region_id: str,
    ac_value: Optional[str] = None,
    rank_data: Optional[bool] = False
) -> ResponseDict:
    '''获取用户的基本数据(name+clan)

    这是一个公用函数，用于获取用户名称、工会以及状态

    参数：
        account_id: 用户id
        region_id: 服务器id
        ac_value: ac值

    返回：
        JSONResponse
    '''

    '''
    请求处理逻辑/
    ├── 1. 从数据库中读取数据(user_basic,user_clan,clan_basic)
    ├── 2. 首次请求接口获取用户和工会的基础数据/
    │   └── (后台任务) 更新user_basic,user_clan和clan_basic表
    ├── 3. 从用户基础数据，判断用户的状态(is_acctive,is_public等)/
    │   └── (后台任务) 更新user_info表
    └── 4. 返回结果
    '''
    # 返回的user和clan数据格式
    user_basic = {
        'id': account_id,
        'region': region_id,
        'name': UtilityFunctions.get_user_default_name(account_id),
        'karma': 0,
        'crated_at': 0,
        'actived_at': 0,
        'dog_tag': {}
    }
    clan_basic = {
        'id': None,
        'tag': None,
        'league': 5
    }
    # 用于后台更新user_info表的数据
    user_info = {
        'account_id': account_id,
        'region_id': region_id,
        'is_active': True,
        'active_level': 0,
        'is_public': True,
        'total_battles': 0,
        'last_battle_time': 0
    }
    basic_data = await BasicAPI.get_user_basic_and_clan(account_id,region_id,ac_value)

    for response in basic_data:
        if response['code'] != 1000 and response['code'] != 1001:
            return response
    # 用户数据
    if basic_data[0]['code'] == 1001:
        # 用户数据不存在
        user_info['is_active'] = False
        celery_app.send_task(
            name="check_user_info",
            args=[user_info]
        )
        return JSONResponse.API_1001_UserNotExist
    user_basic['name'] = basic_data[0]['data'][str(account_id)]['name']
    if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
        # 隐藏战绩
        user_info['is_public'] = False
        user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
        celery_app.send_task(
            name="update_user_clan",
            args=[{
                'account_id': user_basic['id'],
                'clan_id': None
            }]
        )
        celery_app.send_task(
            name="check_user_info",
            args=[user_info]
        )
        if ac_value:
            return JSONResponse.API_1013_ACisInvalid
        else:
            return JSONResponse.API_1005_UserHiddenProfite
    user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
    if (
        user_basic_data == {} or
        user_basic_data['basic'] == {}
    ):
        # 用户没有数据
        user_info['is_active'] = False
        celery_app.send_task(
            name="check_user_info",
            args=[user_info]
        )
        return JSONResponse.API_1006_UserDataisNone
    if user_basic_data['basic']['leveling_points'] == 0:
        # 用户没有数据
        user_info['total_battles'] = 0
        user_info['last_battle_time'] = 0
        user_info['active_level'] = 1
        celery_app.send_task(
            name="check_user_info",
            args=[user_info]
        )
        return JSONResponse.API_1006_UserDataisNone
    # 获取user_info的数据并更新数据库
    user_info['total_battles'] = user_basic_data['basic']['leveling_points']
    user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
    user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
    celery_app.send_task(
        name="check_user_info",
        args=[user_info]
    )
    # 获取user_basic的数据
    user_basic['karma'] = user_basic_data['basic']['karma']
    user_basic['crated_at'] = user_basic_data['basic']['created_at']
    user_basic['actived_at'] = user_basic_data['basic']['last_battle_time']
    user_basic['dog_tag'] = basic_data[0]['data'][str(account_id)]['dog_tag']
    #处理工会信息
    user_clan_data = basic_data[1]['data']
    if user_clan_data['clan_id'] != None:
        clan_basic['id'] = user_clan_data['clan_id']
        clan_basic['tag'] = user_clan_data['clan']['tag']
        clan_basic['league'] = UtilityFunctions.get_league_by_color(user_clan_data['clan']['color'])
        celery_app.send_task(
            name="update_clan_and_user",
            args=[{
                'clan_id': clan_basic['id'],
                'region_id': region_id,
                'tag': clan_basic['tag'],
                'league': clan_basic['league']
            },
            {
                'account_id': user_basic['id'],
                'clan_id': clan_basic['id']
            }]
        )
    else:
        celery_app.send_task(
            name="update_user_clan",
            args=[{
                'account_id': user_basic['id'],
                'clan_id': None
            }]
        )
    # 返回user和clan数据
    if not rank_data:
        data = {
            'user': user_basic,
            'clan': clan_basic
        }
    else:
        rank_basic = season_data(user_basic_data['seasons'], user_basic_data['rank_info'])
        data = {
            'user': user_basic,
            'clan': clan_basic,
            'rank': rank_basic
        }
    return JSONResponse.get_success_response(data)

def season_data(season_data: dict, rank_data: dict) -> dict:
    result = {}
    for season_index in season_data:
        if len(season_index) != 4:
            continue
        result[season_index] = {
            'battles_count': 0, 
            'wins': 0, 
            'damage_dealt': 0,
            'frags': 0, 
            'original_exp': 0, 
            'best_season_rank': 3, 
            'best_rank': 10
        }
        for index in ['battles_count', 'wins', 'damage_dealt', 'frags', 'original_exp']:
            if season_index in ['1001','1002','1003']:
                result[season_index][index] = season_data[str(season_index)]['-1']['rank_solo'][index]
            else:
                result[season_index][index] = season_data[str(season_index)]['0']['rank_solo'][index]
        for _, season_stage_data in rank_data[season_index].items():
            for num in [1, 2, 3]:
                if str(num) in season_stage_data:
                    if result[season_index]['best_season_rank'] > num:
                        result[season_index]['best_season_rank'] = num
                        result[season_index]['best_rank'] = season_stage_data[str(num)]['rank_best']
                        continue
                    elif (
                        result[season_index]['best_season_rank'] == num
                        and result[season_index]['best_rank'] > season_stage_data[str(num)]['rank_best']
                    ):
                        result[season_index]['best_rank'] = season_stage_data[str(num)]['rank_best']
                        continue
                    continue
                else:
                    continue
    sorted_dict = dict(sorted(result.items(), reverse=True))
    return sorted_dict
