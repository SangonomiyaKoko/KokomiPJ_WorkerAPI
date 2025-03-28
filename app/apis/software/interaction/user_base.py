from typing import Optional

from app.utils import UtilityFunctions
from app.network import BasicAPI, MainAPI
from app.response import JSONResponse, ResponseDict
from app.middlewares import CeleryProducer

async def get_user_name_and_clan(
    account_id: int,
    region_id: str,
    ac_value: Optional[str] = None
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
    # 返回的user和clan数据格式
    user_basic = {
        'id': account_id,
        'region': region_id,
        'name': UtilityFunctions.get_user_default_name(account_id),
        'karma': 0,
        'level': 0,
        'created_at': 0,
        'actived_at': 0,
        'dog_tag': {}
    }
    update_data = {
        'region_id': region_id,
        'account_id': account_id,
        'basic': None,
        'info': None,
        'clan': None
    }
    user_name = {
        'nickname': None
    }
    user_info = {
        'is_active': True,
        'is_public': True,
        'total_battles': 0,
        'last_battle_time': 0
    }
    clan_basic = {
        'id': None,
        'tag': None,
        'league': 5
    }
    basic_data = await BasicAPI.get_user_basic_and_clan(account_id,region_id,ac_value)
    for response in basic_data:
        if response['code'] != 1000 and response['code'] != 1001:
            return response
    # 用户数据
    if basic_data[0]['code'] == 1001:
        # 用户数据不存在
        user_info['is_active'] = False
        update_data['info'] = user_info
        CeleryProducer.send_task(
            name="update_user_data",
            args=[update_data],
            queue='task_queue'
        )
        return JSONResponse.API_1001_UserNotExist
    # 处理用户信息
    user_basic['name'] = basic_data[0]['data'][str(account_id)]['name']
    user_name['nickname'] = basic_data[0]['data'][str(account_id)]['name']
    update_data['basic'] = user_name
    #处理工会信息
    user_clan_data = basic_data[1]['data']
    if user_clan_data['clan_id'] != None:
        clan_basic['id'] = user_clan_data['clan_id']
        clan_basic['tag'] = user_clan_data['clan']['tag']
        clan_basic['league'] = UtilityFunctions.get_league_by_color(user_clan_data['clan']['color'])
        update_data['clan'] = clan_basic
    else:
        update_data['clan'] = clan_basic
    if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
        # 隐藏战绩
        user_info['is_public'] = False
        update_data['info'] = user_info
        CeleryProducer.send_task(
            name="update_user_data",
            args=[update_data],
            queue='task_queue'
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
        update_data['info'] = user_info
        CeleryProducer.send_task(
            name="update_user_data",
            args=[update_data],
            queue='task_queue'
        )
        return JSONResponse.API_1006_UserDataisNone
    if user_basic_data['basic']['leveling_points'] == 0:
        # 用户没有数据
        user_info['total_battles'] = 0
        user_info['last_battle_time'] = 0
        update_data['info'] = user_info
        CeleryProducer.send_task(
            name="update_user_data",
            args=[update_data],
            queue='task_queue'
        )
        return JSONResponse.API_1006_UserDataisNone
    # 获取user_info的数据并更新数据库
    user_info['total_battles'] = user_basic_data['basic']['leveling_points']
    user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
    update_data['info'] = user_info
    CeleryProducer.send_task(
        name="update_user_data",
        args=[update_data],
        queue='task_queue'
    )
    # 获取user_basic的数据
    user_basic['karma'] = user_basic_data['basic']['karma']
    user_basic['level'] = user_basic_data['basic']['leveling_tier']
    user_basic['created_at'] = user_basic_data['basic']['created_at']
    user_basic['actived_at'] = user_basic_data['basic']['last_battle_time']
    user_basic['dog_tag'] = basic_data[0]['data'][str(account_id)]['dog_tag']
    # 返回user和clan数据
    data = {
        'user': user_basic,
        'clan': clan_basic
    }
    return JSONResponse.get_success_response(data)
