from app.utils import ShipName,ShipData,Rating_Algorithm
from app.response import JSONResponse, ResponseDict

def process_overall_data(
    account_id: int,
    region_id: int,
    responses: list,
) -> ResponseDict:
    '''处理signature的数据'''
    # 返回数据的格式
    result = {
        'GamePerformance': {},
        'PlayerStatistics': {},
        'rank': {},
        'record': {}
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
        battle_type_list = ['pvp']
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
    ship_info_dict = ShipName.get_ship_info_batch(region_id,'cn',ship_ids)
    # 获取船只服务器数据
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    # 循环计算船只pr
    for ship_id in ship_ids:
        for battle_type in ['pvp']:
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
    overall_data = {
        'AirCarrier': none_processed_data.copy(),
        'Battleship': none_processed_data.copy(),
        'Cruiser': none_processed_data.copy(),
        'Destroyer': none_processed_data.copy(),
        'Submarine': none_processed_data.copy()
    }
    for ship_id in ship_ids:
        for battle_type in ['pvp']:
            # 数据写入，计算出总数据
            ship_data = processed_data.get(ship_id)[battle_type]
            ship_info = ship_info_dict.get(ship_id,None)
            if ship_info is None:
                continue
            ship_type = ship_info['type']
            for index in ['battles_count','wins','damage_dealt','frags','original_exp']:
                overall_data[ship_type][index] += ship_data[index]
            if ship_data['value_battles_count'] > 0:
                for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                    overall_data[ship_type][index] += ship_data[index]
    formatted_data = {
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
        if overall_data[data_type]['value_battles_count'] != 0:
            pr = overall_data[data_type]['personal_rating'] / overall_data[data_type]['value_battles_count']
            if pr >= 2450: tier = 'S'
            elif pr >= 1750: tier = 'A'
            elif pr >= 1450: tier = 'B'
            elif pr >= 1100: tier = 'C'
            else: tier = 'D'
            sum_pr[0] += pr
            sum_pr[1] += 1
            formatted_data[type_dict[data_type]] = tier
    if sum_pr[1]:
        pr = sum_pr[0] / sum_pr[1]
        if pr >= 2450: tier = 'S'
        elif pr >= 1750: tier = 'A'
        elif pr >= 1450: tier = 'B'
        elif pr >= 1100: tier = 'C'
        else: tier = 'D'
        sum_pr[0] += pr
        sum_pr[1] += 1
        formatted_data['Performance_Overall'] = tier
    result['GamePerformance'] = formatted_data
    return JSONResponse.get_success_response(result)