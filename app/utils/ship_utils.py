from typing import List, Set

from app.json import JsonData
from app.const import GameData

class ShipName:
    '''船只相关数据'''
    def __name_format(in_str: str) -> str:
        in_str_list = in_str.split()
        in_str = None
        in_str = ''.join(in_str_list)
        en_list = {
            'a': ['à', 'á', 'â', 'ã', 'ä', 'å'],
            'e': ['è', 'é', 'ê', 'ë'],
            'i': ['ì', 'í', 'î', 'ï'],
            'o': ['ó', 'ö', 'ô', 'õ', 'ò', 'ō'],
            'u': ['ü', 'û', 'ú', 'ù', 'ū'],
            'y': ['ÿ', 'ý'],
            'l': ['ł']
        }
        for en, lar in en_list.items():
            for index in lar:
                if index in in_str:
                    in_str = in_str.replace(index, en)
                if index.upper() in in_str:
                    in_str = in_str.replace(index.upper(), en.upper())
        re_str = ['_', '-', '·', '.', '\'','(',')','（','）']
        for index in re_str:
            if index in in_str:
                in_str = in_str.replace(index, '')
        in_str = in_str.lower()
        return in_str
        
    @classmethod
    def search_ship(cls, ship_name: str, region_id: int, language: str, use_nick: bool):
        '''搜索船只

        参数:
            ship_name: 搜索的名称
            region_id: 服务器id
            language: 搜索的语言
            use_nick：是否使用别名表搜索
        '''
        if region_id == 4:
            server = 'lesta'
        else:
            server = 'wg'
        nick_data = JsonData.read_json_data('ship_name_nick')
        main_data = JsonData.read_json_data(f'ship_name_{server}')
        ship_name_format: str = cls.__name_format(ship_name)
        if ship_name_format.endswith(('old','旧')):
            old = True
        else:
            old = False

        result = []
        # 别名表匹配
        if use_nick:
            for ship_id, ship_data in nick_data[language].items():
                for index in ship_data:
                    if ship_name_format == cls.__name_format(index):
                        result[ship_id] = {
                            "id": ship_id,
                            "tier": main_data[ship_id]['tier'], 
                            "type": main_data[ship_id]['type'], 
                            "nation": main_data[ship_id]['nation'], 
                            "premium": main_data[ship_id]['premium'], 
                            "special": main_data[ship_id]['special'], 
                            "index": main_data[ship_id]['index'], 
                            "ship_name": {
                                'cn': main_data[ship_id]['ship_name']['cn'],
                                'en': main_data[ship_id]['ship_name']['en'],
                                'ja': main_data[ship_id]['ship_name']['ja'],
                                'ru': main_data[ship_id]['ship_name']['ru'],
                                "en_full": main_data[ship_id]['ship_name']['en_l'],
                            }
                        }
                        return result
        for ship_id, ship_data in main_data.items():
            if ship_name_format == cls.__name_format(ship_data['ship_name']['en']):
                result[ship_id] = {
                    'tier':main_data[ship_id]['tier'],
                    'type':main_data[ship_id]['type'],
                    'cn':main_data[ship_id]['ship_name']['cn'],
                    'en':main_data[ship_id]['ship_name']['en'],
                    'ja':main_data[ship_id]['ship_name']['ja'],
                    'ru':main_data[ship_id]['ship_name']['ru']
                }
                return result
            if language in ['cn','ja','ru','en']:
                if language == 'en':
                    lang = 'en_l'
                else:
                    lang = language
                if ship_name_format == cls.__name_format(ship_data['ship_name'][lang]):
                    result[ship_id] = {
                        'tier':main_data[ship_id]['tier'],
                        'type':main_data[ship_id]['type'],
                        'cn':main_data[ship_id]['ship_name']['cn'],
                        'en':main_data[ship_id]['ship_name']['en'],
                        'ja':main_data[ship_id]['ship_name']['ja'],
                        'ru':main_data[ship_id]['ship_name']['ru']
                    }
                    return result
        for ship_id, ship_data in main_data.items():
            if ship_name_format in cls.__name_format(ship_data['ship_name']['en']):
                if old == False and ship_id in GameData.OLD_SHIP_ID_LIST:
                    continue
                result[ship_id] = {
                    'tier':main_data[ship_id]['tier'],
                    'type':main_data[ship_id]['type'],
                    'cn':main_data[ship_id]['ship_name']['cn'],
                    'en':main_data[ship_id]['ship_name']['en'],
                    'ja':main_data[ship_id]['ship_name']['ja'],
                    'ru':main_data[ship_id]['ship_name']['ru']
                }
            if language in ['cn','ja','ru','en']:
                if language == 'en':
                    lang = 'en_l'
                else:
                    lang = language
                if ship_name_format in cls.__name_format(ship_data['ship_name'][lang]):
                    if old == False and ship_id in GameData.OLD_SHIP_ID_LIST:
                        continue
                    result[ship_id] = {
                        'tier':main_data[ship_id]['tier'],
                        'type':main_data[ship_id]['type'],
                        'cn':main_data[ship_id]['ship_name']['cn'],
                        'en':main_data[ship_id]['ship_name']['en'],
                        'ja':main_data[ship_id]['ship_name']['ja'],
                        'ru':main_data[ship_id]['ship_name']['ru']
                    }
        return result
    
    def get_ship_info_batch(region_id: int, language: str, ship_ids: List[int] | Set[int]) -> dict:
        ''''''
        result = {}
        if region_id == 4:
            server = 'lesta'
        else:
            server = 'wg'
        main_data = JsonData.read_json_data(f'ship_name_{server}')
        for ship_id in ship_ids:
            if str(ship_id) in main_data:
                result[ship_id] = {
                    'id': str(ship_id),
                    'tier':main_data[str(ship_id)]['tier'],
                    'type':main_data[str(ship_id)]['type'],
                    'nation':main_data[str(ship_id)]['nation'],
                    'premium':main_data[str(ship_id)]['premium'],
                    'special':main_data[str(ship_id)]['special'],
                    'name':main_data[str(ship_id)]['ship_name'][language],
                    'index':main_data[str(ship_id)]['index']
                }
        return result
