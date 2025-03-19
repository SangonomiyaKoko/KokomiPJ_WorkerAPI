from datetime import datetime

from app.utils import UtilityFunctions
from app.network import BasicAPI, MainAPI
from app.response import JSONResponse, ResponseDict
from app.middlewares.celery import CeleryProducer

async def get_clan_tag_and_league(
    clan_id: int,
    region_id: str
) -> ResponseDict:
    '''获取工会的基本数据(tag+season)

    这是一个公用函数，用于获取工会名称、工会状态

    参数：
        clan_id: 工会id
        region_id: 服务器id

    返回：
        JSONResponse
    '''
    # 返回的user和clan数据格式
    clan_basic = {
        'id': clan_id,
        'tag': UtilityFunctions.get_clan_default_name(),
        'name': None,
        'level': 0,
        'members': 0
    }
    update_date = {
        'region_id': region_id,
        'clan_id': clan_id,
        'basic': None,
        'info': None
    }
    clan_tag = {
        'tag': None,
        'league': None
    }
    # 用于后台更新user_info表的数据
    clan_info = {
        'is_active': True,
        'season_number': 0,
        'public_rating': 1100, 
        'league': 4, 
        'division': 2, 
        'division_rating': 0, 
        'last_battle_at': None
    }
    clan_season = {
        'is_active': True,
        'league': 4, 
        'division': 2, 
        'division_rating': 0, 
        'stage_type': None,
        'stage_process': None
    }
    # 获取claninfo
    basic_data = await BasicAPI.get_clan_basic(clan_id, region_id)
    for response in basic_data:
        if response['code'] != 1000 and response['code'] != 1002:
            return response
    # 工会数据
    if basic_data[0]['code'] == 1002 or 'tag' not in basic_data[0]['data']['clan']:
        # 工会数据不存在
        clan_info['is_active'] = False
        update_date['info'] = clan_info
        CeleryProducer.send_task(
            name="update_clan_data",
            args=[update_date],
            queue='task_queue'
        )
        return JSONResponse.API_1002_ClanNotExist
    # 工会名称改变
    clan_basic['tag'] = basic_data[0]['data']['clan']['tag']
    clan_basic['name'] = basic_data[0]['data']['clan']['name']
    clan_basic['level'] = basic_data[0]['data']['clan']['leveling']
    clan_basic['members'] = basic_data[0]['data']['clan']['members_count']
    # 工会赛季数据
    clan_info['season_number'] = basic_data[0]['data']['wows_ladder']['season_number']
    clan_info['public_rating'] = basic_data[0]['data']['wows_ladder']['public_rating']
    clan_info['league'] = basic_data[0]['data']['wows_ladder']['league']
    clan_info['division'] = basic_data[0]['data']['wows_ladder']['division']
    clan_info['division_rating'] = basic_data[0]['data']['wows_ladder']['division_rating']
    # 工会基本数据
    clan_tag['tag'] = basic_data[0]['data']['clan']['tag']
    clan_tag['league'] = basic_data[0]['data']['wows_ladder']['league']
    update_date['basic'] = clan_tag
    if basic_data[0]['data']['wows_ladder']['last_battle_at']:
        clan_info['last_battle_at'] = int(
            datetime.fromisoformat(basic_data[0]['data']['wows_ladder']['last_battle_at']).timestamp()
        )
    update_date['info'] = clan_info
    if basic_data[0]['data']['wows_ladder']['battles_count'] == 0:
        clan_season['league'] = basic_data[0]['data']['wows_ladder']['league']
        clan_season['division'] = basic_data[0]['data']['wows_ladder']['division']
        clan_season['division_rating'] = basic_data[0]['data']['wows_ladder']['division_rating']
    else:
        season_number = basic_data[0]['data']['wows_ladder']['season_number']
        team_number = basic_data[0]['data']['wows_ladder']['team_number']
        for index in basic_data[0]['data']['wows_ladder']['ratings']:
            if (
                season_number == index['season_number'] and
                team_number == index['team_number']
            ):
                clan_season['league'] = index['league']
                clan_season['division'] = index['division']
                clan_season['division_rating'] = index['division_rating']
                if index['stage'] is None:
                    break
                if index['stage']['type'] == 'promotion':
                    clan_season['stage_type'] = '1'
                else:
                    clan_season['stage_type'] = '2'
                stage_progress = []
                for progress in index['stage']['progress']:
                    if progress == 'victory':
                        stage_progress.append(1)
                    else:
                        stage_progress.append(0)
                clan_season['stage_progress'] = str(stage_progress)
                break
    CeleryProducer.send_task(
        name="update_clan_data",
        args=[update_date],
        queue='task_queue'
    )
    data = {
        'clan': clan_basic,
        'season': clan_season
    }
    return JSONResponse.get_success_response(data)
