from app.utils import ShipName, ShipData, Rating_Algorithm
from app.const import GameData
from app.response import JSONResponse, ResponseDict

def process_overall_data(
    account_id: int,
    region_id: int,
    responses: list,
    rank_data: dict,
    language: str
) -> ResponseDict:
    '''处理signature的数据'''
    # 返回数据的格式
    result = {
        'playerPerformance': {},
        'playerStatistics': {},
        'palyerRankData': {},
        'playerRecord': {}
    }
    none_processed_data = {
        'battles_count': 0,
        'wins': 0,
        'damage_dealt': 0,
        'frags': 0,
        'original_exp': 0,
        'survived': 0, 
        'hits_by_main': 0, 
        'shots_by_main': 0,
        'value_battles_count': 0,
        'personal_rating': 0,
        'n_damage_dealt': 0,
        'n_frags': 0
    }
    record_dict = {
        'max_damage_dealt': {'value': 0, 'vehicle': None},
        'max_exp': {'value': 0, 'vehicle': None},
        'max_frags': {'value': 0, 'vehicle': None},
        'max_planes_killed': {'value': 0, 'vehicle': None},
        'max_scouting_damage': {'value': 0, 'vehicle': None},
        'max_total_agro': {'value': 0, 'vehicle': None}
    }
    processed_data = {} # 处理好的数据
    formatted_data = {} # 格式化好的数据
    ship_ids = set() # 需要处理的ship_id集合
    i = 0
    for response in responses:
        battle_type_list = ['pvp', 'pvp_solo','pvp_div2','pvp_div3','rank_solo']
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
                for index in ['battles_count','wins','damage_dealt','frags','original_exp', 'survived', 'hits_by_main', 'shots_by_main']:
                    processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
            if battle_type == 'pvp':
                for record_index in ['max_damage_dealt', 'max_exp', 'max_frags', 'max_planes_killed', 'max_scouting_damage', 'max_total_agro']:
                    if ship_data[battle_type][record_index] > record_dict[record_index]['value']:
                        record_dict[record_index]['value'] = ship_data[battle_type][record_index]
                        record_dict[record_index]['vehicle'] = ship_id
    # 获取船只的信息
    ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
    # 获取船只服务器数据
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    # 循环计算船只pr
    for ship_id in ship_ids:
        for battle_type in ['pvp', 'pvp_solo','pvp_div2','pvp_div3','rank_solo']:
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
                'pr',
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
    ship_type_data = {
        'AirCarrier': none_processed_data.copy(),
        'Battleship': none_processed_data.copy(),
        'Cruiser': none_processed_data.copy(),
        'Destroyer': none_processed_data.copy(),
        'Submarine': none_processed_data.copy()
    }
    battle_type_data = {
        'pvp': none_processed_data.copy(),
        'pvp_solo': none_processed_data.copy(),
        'pvp_div2': none_processed_data.copy(),
        'pvp_div3': none_processed_data.copy(),
        'rank_solo': none_processed_data.copy()
    }
    battle_type_data['pvp']['tier'] = 0
    battle_type_data['pvp_solo']['tier'] = 0
    battle_type_data['pvp_div2']['tier'] = 0
    battle_type_data['pvp_div3']['tier'] = 0
    battle_type_data['rank_solo']['tier'] = 0
    for ship_id in ship_ids:
        for battle_type in ['pvp']:
            # 数据写入，计算出总数据
            ship_data = processed_data.get(ship_id)[battle_type]
            ship_info = ship_info_dict.get(ship_id,None)
            if ship_info is None:
                continue
            ship_type = ship_info['type']
            for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                ship_type_data[ship_type][index] += ship_data[index]
            if ship_data['value_battles_count'] > 0:
                for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                    ship_type_data[ship_type][index] += ship_data[index]
        for battle_type in ['pvp', 'pvp_solo','pvp_div2','pvp_div3','rank_solo']:
            ship_data = processed_data.get(ship_id)[battle_type]
            ship_info = ship_info_dict.get(ship_id,None)
            if ship_info is None:
                continue
            ship_type = ship_info['type']
            ship_tier = ship_info['tier']
            if ship_data['battles_count']:
                battle_type_data[battle_type]['tier'] += ship_tier * ship_data['battles_count']
            for index in ['battles_count','wins','damage_dealt','frags','original_exp', 'survived', 'hits_by_main', 'shots_by_main']:
                battle_type_data[battle_type][index] += ship_data[index]
            if ship_data['value_battles_count'] > 0:
                for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                    battle_type_data[battle_type][index] += ship_data[index]
    player_performance = {
        "Performance_Overall": "-",
        "Performance_BB": "-",
        "Performance_CA": "-",
        "Performance_DD": "-",
        "Performance_CV": "-",
        "Performance_SS": "-"
    }
    sum_pr = [0, 0]
    for data_type in ['AirCarrier', 'Battleship', 'Cruiser', 'Destroyer', 'Submarine']:
        type_dict = {
            'AirCarrier': 'Performance_CV',
            'Battleship': 'Performance_BB',
            'Cruiser': 'Performance_CA',
            'Destroyer': 'Performance_DD',
            'Submarine': 'Performance_SS',
        }
        if ship_type_data[data_type]['value_battles_count'] != 0:
            pr = ship_type_data[data_type]['personal_rating'] / ship_type_data[data_type]['value_battles_count']
            if pr >= 2450: tier = 'S'
            elif pr >= 1750: tier = 'A'
            elif pr >= 1450: tier = 'B'
            elif pr >= 1100: tier = 'C'
            else: tier = 'D'
            sum_pr[0] += pr
            sum_pr[1] += 1
            player_performance[type_dict[data_type]] = tier
    if sum_pr[1]:
        pr = sum_pr[0] / sum_pr[1]
        if pr >= 2450: tier = 'S'
        elif pr >= 1750: tier = 'A'
        elif pr >= 1450: tier = 'B'
        elif pr >= 1100: tier = 'C'
        else: tier = 'D'
        sum_pr[0] += pr
        sum_pr[1] += 1
        player_performance['Performance_Overall'] = tier
    result['playerPerformance'] = player_performance
    player_statistics = []
    for battle_type in ['pvp', 'pvp_solo','pvp_div2','pvp_div3','rank_solo']:
        processed_data = battle_type_data[battle_type]
        battles_count = processed_data['battles_count']
        temp_data = {
            "data_type": "overallStats" if battle_type == 'pvp' else battle_type,    #数据类型——单人
            "battles_count": str(battles_count),    #总场次
            "win_rate": "0%",    #总胜率
            "avg_damage": "0",   #场均伤害
            "avg_frags": "0",   #场均击杀
            "kd": "0",    #K/D
            "avg_exp": "0",    #场均经验
            "survive_rate": "0",   #存活率
            "avg_tier": '0',   #平均等级
            "avg_battery_hit_ratio": '0%',   #平均主炮命中率
            "rating": "-1",#评分(包括评分色块)
            "rating_next": "-1",#下一级
            "rating_class": "-1",#评分等级
        }
        if battles_count <= 0:
            player_statistics.append(temp_data)
        else:
            temp_data['win_rate'] = str(round(processed_data['wins']/battles_count*100, 1)) + '%'
            temp_data['avg_damage'] = '{:,}'.format(int(processed_data['damage_dealt']/battles_count)).replace(',', ' ')
            temp_data['avg_frags'] = str(round(processed_data['frags']/battles_count, 2))
            dead_counts = processed_data['battles_count'] - processed_data['survived']
            temp_data['kd'] = "999" if dead_counts == 0 else str(round(processed_data['frags']/dead_counts,2))
            temp_data['avg_exp'] = '{:,}'.format(int(processed_data['original_exp']/battles_count)).replace(',', ' ')
            temp_data['survive_rate'] = str(round(processed_data['survived']/battles_count*100, 1)) + '%'
            temp_data['avg_tier'] = str(round(processed_data['tier']/battles_count, 2))
            temp_data['avg_battery_hit_ratio'] = "0.0" if processed_data['shots_by_main'] == 0 else str(round(processed_data['hits_by_main']/processed_data['shots_by_main']*100,1)) + '%'
            if processed_data['value_battles_count'] != 0:
                rating = int(processed_data['personal_rating']/processed_data['value_battles_count'])
                rating_class, rating_next = Rating_Algorithm.get_rating_class('pr',rating)
                temp_data['rating_next'] = str(rating_next)
                temp_data['rating'] = '{:,}'.format(rating).replace(',', ' ')
                temp_data['rating_class'] = str(rating_class)
            player_statistics.append(temp_data)
    result['playerStatistics'] = player_statistics
    const_rank_data = []
    rank_level_dict = {
        1: 'gold',
        2: 'silver',
        3: 'gobronze'
    }
    for season_number in range(1, 23):
        if str(1000+season_number) in rank_data:
            temp_data = {
                "season": str(season_number),
                "rank": rank_level_dict.get(rank_data[str(1000+season_number)]['best_season_rank']),
                "level": str(rank_data[str(1000+season_number)]['best_rank'])
            }
        else:
            temp_data = {
                "season": str(season_number),
                "rank": 'gobronze',
                "level": '10'
            }
        const_rank_data.append(temp_data)
    result['palyerRankData'] = const_rank_data
    player_record = []
    record_name_dict = {
        'max_damage_dealt': 'max_dmg', 
        'max_exp': 'max_xp', 
        'max_frags': 'max_frag', 
        'max_planes_killed': 'max_plane_kill', 
        'max_scouting_damage': 'max_spotdmg', 
        'max_total_agro': 'max_potential'
    }
    ship_name_dict = {
        'AirCarrier': 'cv',
        'Battleship': 'bb',
        'Cruiser': 'ca',
        'Destroyer': 'dd',
        'Submarine': 'ss'
    }
    for record_type in ['max_damage_dealt', 'max_exp', 'max_frags', 'max_planes_killed', 'max_scouting_damage', 'max_total_agro']:
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
            "record_type": record_name_dict.get(record_type),   #最高侦察伤害
            "record_data": '{:,}'.format(record_dict[record_type]['value']).replace(',', ' '),    #实际数字
            "record_ship_tier": GameData.TIER_NAME_LIST.get(ship_tier),    #船只等级
            "record_ship_type": ship_name_dict.get(ship_type),    #船只类型
            "record_ship_id": str(ship_id),     #记录最大值船id
            "record_ship_name": ship_name,    #船名
        }
        player_record.append(temp_data)
    result['playerRecord'] = player_record
    return JSONResponse.get_success_response(result)