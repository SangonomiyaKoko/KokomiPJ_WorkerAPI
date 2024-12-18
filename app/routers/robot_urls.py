from typing import Optional

from fastapi import APIRouter

from app.core import ServiceStatus
from app.response import ResponseDict, JSONResponse
from app.network import ProxyAPI
from app.utils import UtilityFunctions
from app.apis.robot import user_basic
from .schemas import (
    RegionList, LanguageList, AlgorithmList, GameTypeList, 
    PlatformList, BotUserBindModel
)

router = APIRouter()

@router.get("/version/", summary="[Proxy]获取robot的最新版本")
async def getVersion() -> ResponseDict:
    """获取最新版本"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    path = '/r/version/'
    params = {}
    result = await ProxyAPI.get(path=path, params=params)
    return result

@router.get("/user/bind/", summary="[Proxy]获取用户的绑定信息")
async def getUserBind(
    platform: PlatformList,
    user_id: str
) -> ResponseDict:
    """获取用户的绑定信息"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    path = '/r/user/bind/'
    params = {
        'platform': platform.name,
        'user_id': user_id
    }
    result = await ProxyAPI.get(path=path, params=params)
    return result

@router.post("/user/bind/", summary="[Proxy]更新用户的绑定信息")
async def postUserBind(
    user_data: BotUserBindModel
) -> ResponseDict:
    """更新或者写入用户的绑定信息"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    path = '/r/user/bind/'
    params = {}
    data = user_data.model_dump()
    result = await ProxyAPI.post(path=path, params=params, data=data)
    return result

@router.get("/user/account/", summary="用户基本数据")
async def searchUser(
    region: RegionList,
    account_id: int,
    language: LanguageList,
    game_type: GameTypeList,
    algo_type: Optional[AlgorithmList] = None,
    ac_value: Optional[str] = None,
    ac2_value: Optional[str] = None

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
        algo_type=algo_type,
        ac_value=ac_value,
        ac2_value=ac2_value
    )
    return result