from typing import Optional

from fastapi import APIRouter

from app.core import ServiceStatus
from app.response import ResponseDict, JSONResponse
from app.utils import UtilityFunctions
from app.apis.robot import user_basic
from .schemas import RegionList, LanguageList, AlgorithmList, GameTypeList

router = APIRouter()

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
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    language = UtilityFunctions.get_language_code(language)
    result = await user_basic.wws_user_basic(
        account_id=account_id,
        region_id=region_id,
        game_type=game_type,
        language=language,
        algo_type=algo_type,
        ac_value=ac_value,
        ac2_value=ac2_value
    )
    return result