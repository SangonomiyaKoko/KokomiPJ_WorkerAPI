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
    update_datas = []
    for temp_data in response.get('data',None):
        update_data = {
            'region_id': region_id,
            'account_id': temp_data['spa_id'],
            'basic': None,
            'info': None,
            'clan': None
        }
        user_name = {
            'nickname': temp_data['name']
        }
        update_data['basic'] = user_name
        user_info = {
            'is_active': True,
            'is_public': True,
            'total_battles': 0,
            'last_battle_time': 0
        }
        if temp_data['hidden'] == True:
            user_info['is_public'] = False
            update_data['info'] = user_info
            update_datas.append(update_data)
        elif temp_data['statistics'] == {}:
            user_info['is_active'] = False
            update_data['info'] = user_info
            update_datas.append(update_data)
        else:
            update_datas.append(update_data)
    celery_app.send_task(
        name="update_user_data",
        args=[update_datas],
        queue='task_queue'
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
    update_datas = []
    for temp_data in response.get('data', None):
        update_data = {
            'region_id': region_id,
            'clan_id': temp_data['id'],
            'basic': None,
            'info': None
        }
        clan_basic = {
            'tag': temp_data['tag'],
            'league': ClanColor.CLAN_COLOR_INDEX_2.get(temp_data['hex_color'], 5)
        }
        update_data['basic'] = clan_basic
        update_datas.append(update_data)
    celery_app.send_task(
        name="update_clan_data",
        args=[update_datas],
        queue='task_queue'
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