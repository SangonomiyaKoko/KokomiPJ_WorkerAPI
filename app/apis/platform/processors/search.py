from app.response import ResponseDict, JSONResponse
from app.const import ClanColor
from app.middlewares import celery_app

def process_search_user_data(
    region_id: int, 
    nickname: str, 
    response: dict, 
    limit: int,
    check: bool = False
) -> ResponseDict:
    # 获取所有的结果，通过后台任务更新数据库
    for temp_data in response.get('data',None):
        user_basic = {
            'account_id': temp_data['spa_id'],
            'region_id': region_id,
            'nickname': temp_data['name']
        }
        if temp_data['hidden'] == True:
            user_info = {
                'account_id': temp_data['spa_id'],
                'region_id': region_id,
                'is_active': True,
                'active_level': 0,
                'is_public': False,
                'total_battles': 0,
                'last_battle_time': 0
            }
            celery_app.send_task(
                name='check_user_basic_and_info',
                args=[user_basic,user_info],
            )
        elif temp_data['statistics'] == {}:
            user_info = {
                'account_id': temp_data['spa_id'],
                'region_id': region_id,
                'is_active': False,
                'active_level': 0,
                'is_public': True,
                'total_battles': 0,
                'last_battle_time': 0
            }
            celery_app.send_task(
                name='check_user_basic_and_info',
                args=[user_basic,user_info],
            )
        else:
            celery_app.send_task(
                name='check_user_basic',
                args=[user_basic],
            )
    search_data = []
    if check:
        for temp_data in response.get('data',None):
            if nickname == temp_data['name'].lower():
                search_data.append({
                    'account_id':temp_data['spa_id'],
                    'region_id': region_id,
                    'name':temp_data['name']
                })
                break
    else:
        for temp_data in response.get('data',None):
            if len(search_data) > limit:
                break
            search_data.append({
                'account_id':temp_data['spa_id'],
                'region_id': region_id,
                'name':temp_data['name']
            })
    return JSONResponse.get_success_response(search_data)

def process_search_clan_data(
    region_id: int, 
    tag: str,
    response: dict, 
    limit: int,
    check: bool = False
) -> ResponseDict:
    # 获取所有的结果，通过后台任务更新数据库
    for temp_data in response.get('data', None):
        clan_basic = {
            'clan_id': temp_data['id'],
            'region_id': region_id,
            'tag': temp_data['tag'],
            'league': ClanColor.CLAN_COLOR_INDEX_2.get(temp_data['hex_color'], 5)
        }
        celery_app.send_task(
            name='check_clan_basic',
            args=[clan_basic],
        )
    search_data = []
    if check:
        for temp_data in response.get('data',None):
            if tag == temp_data['tag'].lower():
                search_data.append({
                    'clan_id':temp_data['id'],
                    'region_id': region_id,
                    'tag':temp_data['tag']
                })
                break
    else:
        for temp_data in response.get('data',None):
            if len(search_data) > limit:
                break
            if tag in temp_data['tag'].lower():
                search_data.append({
                    'clan_id':temp_data['id'],
                    'region_id': region_id,
                    'tag':temp_data['tag']
                })
    return JSONResponse.get_success_response(search_data)