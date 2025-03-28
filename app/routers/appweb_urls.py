from typing import Optional

from fastapi import APIRouter

from app.core import ServiceStatus
from app.response import ResponseDict, JSONResponse
from app.utils import UtilityFunctions
from app.apis.software import user_page
from .schemas import RegionList, LanguageList

router = APIRouter()

@router.get("/user/page/", summary="用户数据页接口")
async def searchUser(
    region: RegionList,
    account_id: int
) -> ResponseDict:
    """游戏用户数据接口

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
    result = await user_page.user_page(
        account_id=account_id,
        region_id=region_id
    )
    return result