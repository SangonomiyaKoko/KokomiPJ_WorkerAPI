from typing import Optional

from fastapi import APIRouter

from app.core import ServiceStatus
from app.response import ResponseDict, JSONResponse
from app.network import ProxyAPI
from app.utils import UtilityFunctions
from app.apis.robot import user_basic, user_bind, leaderboard
from .schemas import (
    RegionList, LanguageList, AlgorithmList, GameTypeList, 
    PlatformList, BotUserBindModel, RankRegionList
)

router = APIRouter()

@router.get("/version/", summary="获取robot的最新版本")
async def getVersion() -> ResponseDict:
    """获取最新版本"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    path = '/r/version/'
    params = {}
    result = await ProxyAPI.get(path=path, params=params)
    return result

@router.get("/user/bind/", summary="获取用户的绑定信息")
async def getUserBind(
    platform: PlatformList,
    user_id: str
) -> ResponseDict:
    """获取用户的绑定信息"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    result = await user_bind.get_user_bind(platform.name, user_id)
    return result

@router.post("/user/bind/", summary="更新用户的绑定信息")
async def postUserBind(
    user_data: BotUserBindModel
) -> ResponseDict:
    """更新或者写入用户的绑定信息"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    data = user_data.model_dump()
    result = await user_bind.post_user_bind(data)
    return result

@router.get("/user/account/", summary="用户基本数据")
async def searchUser(
    region: RegionList,
    account_id: int,
    language: LanguageList,
    game_type: GameTypeList,
    algo_type: Optional[AlgorithmList] = None
) -> ResponseDict:
    """游戏用户数据接口

    搜索输入的用户名称

    参数:
        ......

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    language = UtilityFunctions.get_language_code(language.name)
    result = await user_basic.wws_user_basic(
        account_id=account_id,
        region_id=region_id,
        game_type=game_type.name,
        language=language,
        algo_type=algo_type
    )
    return result

@router.get("/leaderboard/page/{region_id}/{ship_id}/", summary="获取排行榜单页数据")
async def get_leaderboard(
    region: RankRegionList,
    ship_id: int,
    language: LanguageList,
    page_idx: int = 1,
    page_zise: int = 100
) -> ResponseDict:
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_idx = UtilityFunctions.get_region_idx(region.name)
    if region_idx not in [0, 1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    language = UtilityFunctions.get_language_code(language.name)
    result = await leaderboard.get_leaderboard_page(
        region_idx=region_idx,
        ship_id=ship_id,
        page_idx=page_idx,
        page_size=page_zise,
        language=language
    )
    return result

@router.get("/leaderboard/user/{region_id}/{ship_id}/{account_id}/", summary="获取用户的单表排名")
async def get_user_rank(
    region: RegionList,
    account_id: int,
    region2: RankRegionList,
    ship_id: int,
    language: LanguageList
) -> ResponseDict:
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    region_idx = UtilityFunctions.get_region_idx(region2.name)
    if region_idx not in [0, 1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    language = UtilityFunctions.get_language_code(language.name)
    result = await leaderboard.get_user_leaderboard_data(
        region_idx=region_idx,
        ship_id=ship_id,
        region_id=region_id,
        account_id=account_id,
        language=language
    )
    return result