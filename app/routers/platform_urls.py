from typing import Optional

from fastapi import APIRouter

from app.core import ServiceStatus
from app.response import ResponseDict, JSONResponse
from app.utils import UtilityFunctions
from app.apis.platform import SearchID
from .schemas import RegionList, LanguageList

router = APIRouter()

@router.get("/search/user/", summary="搜索用户")
async def searchUser(
    region: RegionList,
    nickname: str,
    limit: Optional[int] = 10,
    check: Optional[bool] = False
) -> ResponseDict:
    """用户搜索接口

    搜索输入的用户名称

    参数:
    - region: 服务器
    - nickname: 搜索的名称
    - limit: 搜索返回值的限制
    - check: 是否检查并返回唯一合适的结果

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if not 3 <= len(nickname) <= 25:
        return JSONResponse.API_1011_IllegalUserName
    result = await SearchID.search_user(
        region_id = region_id,
        nickname = nickname.lower(),
        limit = limit,
        check = check
    )
    return result

@router.get("/search/clan/", summary="搜索工会")
async def searchClan(
    region: RegionList,
    tag: str,
    limit: Optional[int] = 10,
    check: Optional[bool] = False
) -> ResponseDict:
    """工会搜索接口

    搜索输入的工会名称

    参数:
    - region: 服务器
    - tag: 搜索的名称
    - limit: 搜索返回值的限制
    - check: 是否检查并返回唯一合适的结果

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if not 2 <= len(tag) <= 5:
        return JSONResponse.API_1012_IllegalClanTag
    result = await SearchID.search_clan(
        region_id = region_id,
        tag = tag.lower(),
        limit = limit,
        check = check
    )
    return result

@router.get("/search/ship/", summary="搜索船只")
async def searchShip(
    region: RegionList,
    language: LanguageList,
    shipname: str,
    use_nick: bool = True
) -> ResponseDict:
    """船只搜索接口

    搜索输入的船只名称

    参数:
    - region: 服务器
    - language: 搜索的语言
    - shipname: 搜索的名称

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    language = UtilityFunctions.get_language_code(language)
    result = await SearchID.search_ship(
        region_id = region_id,
        ship_name = shipname,
        language = language,
        use_nick = use_nick
    )
    return result