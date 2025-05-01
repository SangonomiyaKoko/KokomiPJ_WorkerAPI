from app.utils import ShipName,ShipData,Rating_Algorithm, ColorUtils
from app.response import JSONResponse, ResponseDict
from app.const import GameData
from .user_base import BaseFormatData

def process_signature_data(
    account_id: int,
    region_id: int,
    responses: list,
    language: str,
    algo_type: str = None
) -> ResponseDict:
    '''处理signature的数据
    
    处理流程：处理原始数据 -> 数据格式化 -> 返回处理好数据
    '''
    # 返回数据的格式
    result = {
        'total': {},
        'stats': {},
        'record': {},
        'achievement': {}
    }
    none_processed_data = {
        'battles_count': 0,
        'wins': 0,
        'damage_dealt': 0,
        'frags': 0,
        'value_battles_count': 0,
        'personal_rating': 0,
        'n_damage_dealt': 0,
        'n_frags': 0
    }
    
    record_dict = {
        'max_damage_dealt': {'value': 0, 'vehicle': None},
        'max_exp': {'value': 0, 'vehicle': None},
        'max_frags': {'value': 0, 'vehicle': None},
        'max_planes_killed': {'value': 0, 'vehicle': None}
    }
    achievement_dict = {
        'ranked': {},
        'clan_battle': {}
    }
    total_ach = 0
    processed_data = {} # 处理好的数据
    formatted_data = {} # 格式化好的数据
    ship_ids = set() # 需要处理的ship_id集合
    i = 0
    for response in responses:
        if i == 0:
            battle_type = 'pvp'
        elif i == 1:
            battle_type = 'rank_solo'
        else:
            rank_dict = {
                '0': 0, '1': 0, '2': 0
            }
            cw_dict = {
                '0': 0, '1': 0, '2': 0,
                '3': 0, '4': 0
            }
            achievement_data = response['data'][str(account_id)]['statistics']['achievements']
            for ach_id, ach_data in achievement_data.items():
                if region_id == 4:
                    cw_achievement_dict = GameData.lesta_cw_achievement_dict
                else:
                    cw_achievement_dict = GameData.wg_cw_achievement_dict
                if ach_id in cw_achievement_dict:
                    if cw_achievement_dict[ach_id] == '0':
                        print(ach_id)
                    cw_dict[cw_achievement_dict[ach_id]] += ach_data['count']
                    continue
                if ach_id in GameData.rank_achievement_dict:
                    rank_dict[GameData.rank_achievement_dict[ach_id]] += ach_data['count']
                total_ach += ach_data['count']
            achievement_dict['ranked'] = rank_dict
            achievement_dict['clan_battle'] = cw_dict
            break
        i += 1
        for ship_id, ship_data in response['data'][str(account_id)]['statistics'].items():
            # 读取并保留原始数据中需要的数据
            ship_id = int(ship_id)
            if ship_id not in ship_ids:
                ship_ids.add(ship_id)
                processed_data[ship_id] = {}
            processed_data[ship_id][battle_type] = none_processed_data.copy()
            if (
                ship_data[battle_type] == {} or 
                ship_data[battle_type]['battles_count'] == 0
            ):
                continue
            if ship_data[battle_type] != {}:
                for index in ['battles_count','wins','damage_dealt','frags']:
                    processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
                for record_index in ['max_damage_dealt', 'max_exp', 'max_frags', 'max_planes_killed']:
                    if ship_data[battle_type][record_index] > record_dict[record_index]['value']:
                        record_dict[record_index]['value'] = ship_data[battle_type][record_index]
                        record_dict[record_index]['vehicle'] = ship_id
    # 获取船只的信息
    ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
    # 获取船只服务器数据
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    # 循环计算船只pr
    for ship_id in ship_ids:
        for battle_type in ['pvp', 'rank_solo']:
            ship_data = processed_data.get(ship_id)[battle_type]
            # 用户数据
            account_data = [
                ship_data['battles_count'],
                ship_data['wins'],
                ship_data['damage_dealt'],
                ship_data['frags']
            ]
            # 服务器数据
            if ship_data_dict.get(ship_id):
                server_data = ship_data_dict.get(ship_id)
            else:
                server_data = None
            # 计算评分
            rating_data = Rating_Algorithm.get_rating_by_data(
                algo_type,
                battle_type,
                account_data,
                server_data
            )
            if rating_data[0] > 0:
                # 数据有效则写入
                processed_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
                processed_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
                processed_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
                processed_data[ship_id][battle_type]['n_frags'] += rating_data[3]
    # 中间变量，用于存放计算好的数据
    overall_data = {
        'random': none_processed_data.copy(),
        'ranked': none_processed_data.copy()
    }
    for ship_id in ship_ids:
        for battle_type in ['pvp', 'rank_solo']:
            # 数据写入，计算出总数据
            ship_data = processed_data.get(ship_id)[battle_type]
            if battle_type == 'pvp':
                battle_type = 'random'
            else:
                battle_type = 'ranked'
            ship_info = ship_info_dict.get(ship_id,None)
            if ship_info is None:
                continue
            for index in ['battles_count','wins','damage_dealt','frags']:
                overall_data[battle_type][index] += ship_data[index]
            if ship_data['value_battles_count'] > 0:
                for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                    overall_data[battle_type][index] += ship_data[index]
    for record_type in ['max_damage_dealt', 'max_exp', 'max_frags', 'max_planes_killed']:
        if record_dict[record_type]['vehicle'] == None:
            continue
        ship_id = record_dict[record_type]['vehicle']
        ship_info = ship_info_dict.get(ship_id,None)
        if ship_info is None:
            ship_tier = 1
            ship_type = 'Cruiser'
            ship_name = 'UnknowShip'
        else:
            ship_tier = ship_info['tier']
            ship_type = ship_info['type']
            ship_name = ship_info['name']

        temp_data = {
            "count": '{:,}'.format(record_dict[record_type]['value']).replace(',', ' '),    #实际数字
            "tier": GameData.TIER_NAME_LIST.get(ship_tier),    #船只等级
            "name": ship_name,    #船名
        }
        record_dict[record_type] = temp_data
    formatted_data = {
        'random': {},
        'ranked': {}
    }
    if (
        overall_data['random']['battles_count'] == 0 and 
        overall_data['ranked']['battles_count'] == 0
    ):
        return JSONResponse.API_1006_UserDataisNone
    for battle_type in ['random', 'ranked']:
        # 数据格式化
        formatted_data[battle_type] = BaseFormatData.format_card_processed_data(
            algo_type = algo_type,
            processed_data = overall_data[battle_type]
        )
    result ['record'] = record_dict
    result['stats'] = formatted_data
    result['total'] = {
        'battles_count': 0,
        'ships_count': '{:,}'.format(len(ship_ids)).replace(',', ' '),
        'achievements_count': '{:,}'.format(total_ach).replace(',', ' ')
    }
    result['achievement'] = achievement_dict
    return JSONResponse.get_success_response(result)

def process_lifetime_data(
    account_id: int,
    region_id: int,
    responses: list,
    language: str,
    algo_type: str = None
) -> ResponseDict:
    result = {
        'overall': {},
        'lifetime': {}
    }
    processed_data = {}
    formatted_data = {}
    ship_ids = set()
    response = responses[0]
    battle_type = 'pvp'
    for ship_id, ship_data in response['data'][str(account_id)]['statistics'].items():
        if (
            ship_data[battle_type] == {} or 
            ship_data[battle_type]['battles_count'] == 0
        ):
            continue
        ship_id = int(ship_id)
        ship_ids.add(ship_id)
        processed_data[ship_id] = {}
        processed_data[ship_id][battle_type] = {
            'battles_count': 0,
            'wins': 0,
            'damage_dealt': 0,
            'frags': 0,
            'value_battles_count': 0,
            'personal_rating': 0,
            'n_damage_dealt': 0,
            'n_frags': 0
        }
        if ship_data[battle_type] != {}:
            for index in ['battles_count','wins','damage_dealt','frags']:
                processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
    lifetime_data = {
        'lifetime': None
    }
    response = responses[1]
    if (
        response['status'] == 'ok' and 
        response['data'] != None and 
        response['data'][str(account_id)] != None
    ):
        lifetime_data['lifetime'] = response['data'][str(account_id)]['private']['battle_life_time']
    else:
        return JSONResponse.API_1020_AC2isInvalid
    ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    for ship_id in ship_ids:
        ship_data = processed_data.get(ship_id)[battle_type]
        account_data = [
            ship_data['battles_count'],
            ship_data['wins'],
            ship_data['damage_dealt'],
            ship_data['frags']
        ]
        if ship_data_dict.get(ship_id):
            server_data = ship_data_dict.get(ship_id)
        else:
            server_data = None
        rating_data = Rating_Algorithm.get_rating_by_data(
            algo_type,
            battle_type,
            account_data,
            server_data
        )
        if rating_data[0] > 0:
            processed_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
            processed_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
            processed_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
            processed_data[ship_id][battle_type]['n_frags'] += rating_data[3]
    overall_data = {
        'battles_count': 0,
        'wins': 0,
        'damage_dealt': 0,
        'frags': 0,
        'value_battles_count': 0,
        'personal_rating': 0,
        'n_damage_dealt': 0,
        'n_frags': 0
    }
    for ship_id in ship_ids:
        ship_data = processed_data.get(ship_id)[battle_type]
        ship_info = ship_info_dict.get(ship_id,None)
        if ship_info is None:
            continue
        for index in ['battles_count','wins','damage_dealt','frags']:
            overall_data[index] += ship_data[index]
        if ship_data['value_battles_count'] > 0:
            for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                overall_data[index] += ship_data[index]
    if overall_data['battles_count'] == 0:
        return JSONResponse.API_1006_UserDataisNone
    else:
        formatted_data = BaseFormatData.format_basic_processed_data(
            algo_type = algo_type,
            processed_data = overall_data
        )
    translations = {
        "en": ["Hour", "Minute", "Second"],
        "cn": ["小时", "分钟", "秒"],
        "ja": ["時間", "分", "秒"]
    }
    lifetime_seconds = lifetime_data['lifetime']
    words = translations.get(language, translations["en"])
    hours = lifetime_seconds // 3600
    minutes = (lifetime_seconds % 3600) // 60
    seconds = lifetime_seconds % 60
    lifetime_data['lifetime'] = f"{hours} {words[0]}  {minutes} {words[1]}  {seconds} {words[2]}"

    result['lifetime'] = lifetime_data
    result['overall'] = formatted_data
    return JSONResponse.get_success_response(result)

def process_overall_data(
    account_id: int,
    region_id: int,
    responses: list,
    language: str,
    algo_type: str = None,
    filter_type: str = None
) -> ResponseDict:
    '''处理signature的数据'''
    # 返回数据的格式
    if not filter_type:
        result = {
            'overall': {},
            'battle_type': {},
            'ship_type': {},
            'chart_data': {}
        }
        none_processed_data = {
            'battles_count': 0,
            'wins': 0,
            'damage_dealt': 0,
            'frags': 0,
            'original_exp': 0,
            'value_battles_count': 0,
            'personal_rating': 0,
            'n_damage_dealt': 0,
            'n_frags': 0
        }
        processed_data = {} # 处理好的数据
        formatted_data = {} # 格式化好的数据
        ship_ids = set() # 需要处理的ship_id集合
        i = 0
        for response in responses:
            battle_type_list = ['pvp_solo','pvp_div2','pvp_div3','rank_solo']
            battle_type = battle_type_list[i]
            i += 1
            for ship_id, ship_data in response['data'][str(account_id)]['statistics'].items():
                # 读取并保留原始数据中需要的数据
                ship_id = int(ship_id)
                if ship_id not in ship_ids:
                    ship_ids.add(ship_id)
                    processed_data[ship_id] = {}
                processed_data[ship_id][battle_type] = none_processed_data.copy()
                if (
                    ship_data[battle_type] == {} or 
                    ship_data[battle_type]['battles_count'] == 0
                ):
                    continue
                if ship_data[battle_type] != {}:
                    for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                        processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
        # 获取船只的信息
        ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
        # 获取船只服务器数据
        ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
        # 循环计算船只pr
        for ship_id in ship_ids:
            for battle_type in ['pvp_solo','pvp_div2','pvp_div3','rank_solo']:
                ship_data = processed_data.get(ship_id)[battle_type]
                # 用户数据
                account_data = [
                    ship_data['battles_count'],
                    ship_data['wins'],
                    ship_data['damage_dealt'],
                    ship_data['frags']
                ]
                # 服务器数据
                if ship_data_dict.get(ship_id):
                    server_data = ship_data_dict.get(ship_id)
                else:
                    server_data = None
                # 计算评分
                rating_data = Rating_Algorithm.get_rating_by_data(
                    algo_type,
                    battle_type,
                    account_data,
                    server_data
                )
                if rating_data[0] > 0:
                    # 数据有效则写入
                    processed_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
                    processed_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
                    processed_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
                    processed_data[ship_id][battle_type]['n_frags'] += rating_data[3]
        overall_data = {
            'overall': none_processed_data.copy(),
            'battle_type': {
                'pvp_solo': none_processed_data.copy(),
                'pvp_div2': none_processed_data.copy(),
                'pvp_div3': none_processed_data.copy(),
                'rank_solo': none_processed_data.copy()
            },
            'ship_type': {
                'AirCarrier': none_processed_data.copy(),
                'Battleship': none_processed_data.copy(),
                'Cruiser': none_processed_data.copy(),
                'Destroyer': none_processed_data.copy(),
                'Submarine': none_processed_data.copy()
            },
            'chart_data': {
                '1': 0, '2': 0, '3': 0, '4': 0, 
                '5': 0, '6': 0, '7': 0, '8': 0, 
                '9': 0, '10': 0, '11': 0
            }
        }
        for ship_id in ship_ids:
            for battle_type in ['pvp_solo','pvp_div2','pvp_div3','rank_solo']:
                # 数据写入，计算出总数据
                ship_data = processed_data.get(ship_id)[battle_type]
                ship_info = ship_info_dict.get(ship_id,None)
                if ship_info is None:
                    continue
                ship_tier = ship_info['tier']
                ship_type = ship_info['type']
                for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                    overall_data['battle_type'][battle_type][index] += ship_data[index]
                    if battle_type != 'rank_solo':
                        overall_data['ship_type'][ship_type][index] += ship_data[index]
                if ship_data['value_battles_count'] > 0:
                    for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                        overall_data['battle_type'][battle_type][index] += ship_data[index]
                        if battle_type != 'rank_solo':
                            overall_data['ship_type'][ship_type][index] += ship_data[index]
                if battle_type != 'rank_solo':
                    if ship_data['battles_count'] > 0:
                        overall_data['chart_data'][str(ship_tier)] += ship_data['battles_count']
                    for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                        overall_data['overall'][index] += ship_data[index]
                    if ship_data['value_battles_count'] > 0:
                        for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                            overall_data['overall'][index] += ship_data[index]
        if overall_data['overall']['battles_count'] == 0:
            return JSONResponse.API_1006_UserDataisNone
        formatted_data = {
            'overall': {},
            'battle_type': {
                'pvp_solo': {},
                'pvp_div2': {},
                'pvp_div3': {},
                'rank_solo': {}
            },
            'ship_type': {
                'AirCarrier': {},
                'Battleship': {},
                'Cruiser': {},
                'Destroyer': {},
                'Submarine': {}
            }
        }
        formatted_data['overall'] = BaseFormatData.format_basic_processed_data(
            algo_type = algo_type,
            processed_data = overall_data['overall'],
            show_eggshell = True,
            show_rating_details = True
        )
        for index in ['pvp_solo','pvp_div2','pvp_div3','rank_solo']:
            formatted_data['battle_type'][index] = BaseFormatData.format_basic_processed_data(
                algo_type = algo_type,
                processed_data = overall_data['battle_type'][index],
                show_eggshell = False,
                show_rating_details = True
            )
        for index in ['AirCarrier','Battleship','Cruiser','Destroyer','Submarine']:
            formatted_data['ship_type'][index] = BaseFormatData.format_basic_processed_data(
                algo_type = algo_type,
                processed_data = overall_data['ship_type'][index],
                show_eggshell = False,
                show_rating_details = True
            )
        
        for battle_type in ['overall', 'battle_type', 'ship_type']:
            result[battle_type] = formatted_data[battle_type]
        result['chart_data'] = overall_data['chart_data']
        return JSONResponse.get_success_response(result)
    else:
        is_ranked = False
        filter_battle_type = None
        filter_ship_type = None
        if filter_type == 'rank':
            is_ranked = True
        elif filter_type in ['pvp_solo', 'pvp_div2', 'pvp_div3']:
            filter_battle_type = filter_type
        elif filter_type in ['AirCarrier','Battleship','Cruiser','Destroyer','Submarine','SurfaceShips']:
            filter_ship_type = filter_type
        else:
            pass
        result = {
            'data_type': filter_type,
            'overall': {},
            'battle_type': {},
            'ship_type': {},
            'chart_data': {}
        }
        none_processed_data = {
            'battles_count': 0,
            'wins': 0,
            'damage_dealt': 0,
            'frags': 0,
            'original_exp': 0,
            'value_battles_count': 0,
            'personal_rating': 0,
            'n_damage_dealt': 0,
            'n_frags': 0
        }
        processed_data = {} # 处理好的数据
        formatted_data = {} # 格式化好的数据
        ship_ids = set() # 需要处理的ship_id集合
        i = 0
        for response in responses:
            battle_type_list = ['pvp_solo','pvp_div2','pvp_div3','rank_solo']
            battle_type = battle_type_list[i]
            i += 1
            for ship_id, ship_data in response['data'][str(account_id)]['statistics'].items():
                # 读取并保留原始数据中需要的数据
                ship_id = int(ship_id)
                if ship_id not in ship_ids:
                    ship_ids.add(ship_id)
                    processed_data[ship_id] = {}
                processed_data[ship_id][battle_type] = none_processed_data.copy()
                if (
                    ship_data[battle_type] == {} or 
                    ship_data[battle_type]['battles_count'] == 0
                ):
                    continue
                if ship_data[battle_type] != {}:
                    for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                        processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
        # 获取船只的信息
        ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
        # 获取船只服务器数据
        ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
        # 循环计算船只pr
        for ship_id in ship_ids:
            for battle_type in ['pvp_solo','pvp_div2','pvp_div3','rank_solo']:
                ship_data = processed_data.get(ship_id)[battle_type]
                # 用户数据
                account_data = [
                    ship_data['battles_count'],
                    ship_data['wins'],
                    ship_data['damage_dealt'],
                    ship_data['frags']
                ]
                # 服务器数据
                if ship_data_dict.get(ship_id):
                    server_data = ship_data_dict.get(ship_id)
                else:
                    server_data = None
                # 计算评分
                rating_data = Rating_Algorithm.get_rating_by_data(
                    algo_type,
                    battle_type,
                    account_data,
                    server_data
                )
                if rating_data[0] > 0:
                    # 数据有效则写入
                    processed_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
                    processed_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
                    processed_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
                    processed_data[ship_id][battle_type]['n_frags'] += rating_data[3]
        overall_data = {
            'overall': none_processed_data.copy(),
            'battle_type': {
                'solo': none_processed_data.copy(),
                'div2': none_processed_data.copy(),
                'div3': none_processed_data.copy(),
            },
            'ship_type': {
                'AirCarrier': none_processed_data.copy(),
                'Battleship': none_processed_data.copy(),
                'Cruiser': none_processed_data.copy(),
                'Destroyer': none_processed_data.copy(),
                'Submarine': none_processed_data.copy()
            },
            'chart_data': {
                '1': 0, '2': 0, '3': 0, '4': 0, 
                '5': 0, '6': 0, '7': 0, '8': 0, 
                '9': 0, '10': 0, '11': 0
            }
        }
        for ship_id in ship_ids:
            # 数据写入，计算出总数据
            ship_info = ship_info_dict.get(ship_id,None)
            if ship_info is None:
                continue
            ship_tier = ship_info['tier']
            ship_type = ship_info['type']
            if is_ranked:
                ship_data = processed_data.get(ship_id)['rank_solo']
                for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                    overall_data['battle_type']['solo'][index] += ship_data[index]
                    overall_data['ship_type'][ship_type][index] += ship_data[index]
                if ship_data['value_battles_count'] > 0:
                    for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                        overall_data['battle_type']['solo'][index] += ship_data[index]
                        overall_data['ship_type'][ship_type][index] += ship_data[index]
                if ship_data['battles_count'] > 0:
                    overall_data['chart_data'][str(ship_tier)] += ship_data['battles_count']
                for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                    overall_data['overall'][index] += ship_data[index]
                if ship_data['value_battles_count'] > 0:
                    for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                        overall_data['overall'][index] += ship_data[index]
            else:
                if filter_battle_type:
                    battle_type_list = [filter_battle_type]
                else:
                    battle_type_list = ['pvp_solo','pvp_div2','pvp_div3']
                if filter_ship_type:
                    if filter_ship_type == 'SurfaceShips':
                        ship_type_list = ['Battleship','Cruiser','Destroyer']
                    else:
                        ship_type_list = [filter_ship_type]
                else:
                    ship_type_list = ['AirCarrier','Battleship','Cruiser','Destroyer','Submarine']
                battle_type_dict = {
                    'pvp_solo': 'solo',
                    'pvp_div2': 'div2',
                    'pvp_div3': 'div3'
                }
                for battle_type in battle_type_list:
                    ship_data = processed_data.get(ship_id)[battle_type]
                    if ship_type not in ship_type_list:
                        break
                    for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                        overall_data['battle_type'][battle_type_dict.get(battle_type)][index] += ship_data[index]
                        overall_data['ship_type'][ship_type][index] += ship_data[index]
                    if ship_data['value_battles_count'] > 0:
                        for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                            overall_data['battle_type'][battle_type_dict.get(battle_type)][index] += ship_data[index]
                            overall_data['ship_type'][ship_type][index] += ship_data[index]
                    if ship_data['battles_count'] > 0:
                        overall_data['chart_data'][str(ship_tier)] += ship_data['battles_count']
                    for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                        overall_data['overall'][index] += ship_data[index]
                    if ship_data['value_battles_count'] > 0:
                        for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                            overall_data['overall'][index] += ship_data[index]
        if overall_data['overall']['battles_count'] == 0:
            return JSONResponse.API_1006_UserDataisNone
        formatted_data = {
            'overall': {},
            'battle_type': {
                'solo': {},
                'div2': {},
                'div3': {}
            },
            'ship_type': {
                'AirCarrier': {},
                'Battleship': {},
                'Cruiser': {},
                'Destroyer': {},
                'Submarine': {}
            }
        }
        formatted_data['overall'] = BaseFormatData.format_basic_processed_data(
            algo_type = algo_type,
            processed_data = overall_data['overall'],
            show_eggshell = True,
            show_rating_details = True
        )
        for index in ['solo','div2','div3']:
            formatted_data['battle_type'][index] = BaseFormatData.format_basic_processed_data(
                algo_type = algo_type,
                processed_data = overall_data['battle_type'][index],
                show_eggshell = False,
                show_rating_details = True
            )
        for index in ['AirCarrier','Battleship','Cruiser','Destroyer','Submarine']:
            formatted_data['ship_type'][index] = BaseFormatData.format_basic_processed_data(
                algo_type = algo_type,
                processed_data = overall_data['ship_type'][index],
                show_eggshell = False,
                show_rating_details = True
            )
        
        for battle_type in ['overall', 'battle_type', 'ship_type']:
            result[battle_type] = formatted_data[battle_type]
        result['chart_data'] = overall_data['chart_data']
        return JSONResponse.get_success_response(result)