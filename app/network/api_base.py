from app.core.config import EnvConfig

VORTEX_API_URL_LIST = {
    1: 'https://vortex.worldofwarships.asia',
    2: 'https://vortex.worldofwarships.eu',
    3: 'https://vortex.worldofwarships.com',
    4: 'https://vortex.korabli.su',
    5: 'https://vortex.wowsgame.cn'
}

OFFICIAL_API_URL_LIST = {
    1: 'https://api.worldofwarships.asia',
    2: 'https://api.worldofwarships.eu',
    3: 'https://api.worldofwarships.com',
    4: 'https://api.korabli.su',
    5: None
}

CLAN_API_URL_LIST = {
    1: 'https://clans.worldofwarships.asia',
    2: 'https://clans.worldofwarships.eu',
    3: 'https://clans.worldofwarships.com',
    4: 'https://clans.korabli.su',
    5: 'https://clans.wowsgame.cn'
}

config = EnvConfig.get_config()

proxy_config = {
    '43.133.59.53:8080': [1,2,3,4,5]
}

proxy_list = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}

for key, value in proxy_config.items():
    for region in value:
        proxy_list[region].append(key)

class BaseUrl:
    REQUEST_TIME_OUT = 5
    PROXY_TIME_OUT = 20

    def get_vortex_base_url(region_id: int):
        '''获取vortex api接口的url

        根据代理配置和服务器返回对应的url
        
        如果某个服务器下有多个可用代理则会随机选择一个返回

        参数：
            region: 接口服务器

        返回：
            url: str
        '''
        return VORTEX_API_URL_LIST.get(region_id)
        
    def get_official_base_url(region_id: int):
        '''获取official api接口的url

        不使用代理服务

        参数：
            region: 接口服务器

        返回：
            url: str
        '''
        if region_id == 4:
            api_token = config.LESTA_API_TOKEN
        else:
            api_token = config.WG_API_TOKEN
        return OFFICIAL_API_URL_LIST.get(region_id), api_token
        
    def get_clan_basse_url(region_id: int):
        '''获取clan api接口的url

        根据代理配置和服务器返回对应的url
        
        如果某个服务器下有多个可用代理则会随机选择一个返回

        参数：
            region: 接口服务器

        返回：
            url: str
        '''
        return CLAN_API_URL_LIST.get(region_id)
        
