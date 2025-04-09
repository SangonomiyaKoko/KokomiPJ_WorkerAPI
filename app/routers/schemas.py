from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class RegionList(str, Enum):
    '''
    关于region和region_id的区别

    region主要是用于和前端相关进行交互

    region_id主要是后端处理时使用
    '''
    asia = "asia"
    eu = "eu"
    na = "na"
    ru = "ru"
    cn = "cn"

class RankRegionList(str, Enum):
    '''
    关于region和region_id的区别

    region主要是用于和前端相关进行交互

    region_id主要是后端处理时使用
    '''
    all = "all"
    asia = "asia"
    eu = "eu"
    na = "na"
    ru = "ru"
    cn = "cn"

class PlatformList(str, Enum):
    qq_bot = 'qq_bot'
    qq_group = 'qq_group'
    qq_guild = 'qq_guild'
    discord = 'discord'

class LanguageList(str, Enum):
    chinese = 'chinese'
    english = 'english'
    japanese = 'japanese'
    # 俄语仅在搜索船只接口可用其他接口不支持
    russian = 'russian'

class AlgorithmList(str, Enum):
    pr = 'pr'


class BasicFilterList(str, Enum):
    pvp = 'random'
    rank = 'ranked'
    pvp_solo = 'pvp_solo'
    pvp_div2 = 'pvp_div2'
    pvp_div3 = 'pvp_div3'
    AirCarrier = 'aircarrier'
    Battleship = 'battleship'
    Cruiser = 'cruiser'
    Destroyer = 'destroyer'
    Submarine = 'submarine'
    SurfaceShips = 'surface_ships'


class BotUserBindModel(BaseModel):
    platform: str = Field(..., description='平台')
    user_id: str = Field(..., description='用户id')
    region_id: int = Field(..., description='服务器id')
    account_id: int = Field(..., description='用户id')
