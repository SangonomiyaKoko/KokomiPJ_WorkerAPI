from app.network import BasicAPI
from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.utils import ShipName
from ..processors.search import (
    process_search_user_data,
    process_search_clan_data
)


class SearchID:
    @ExceptionLogger.handle_program_exception_async
    async def search_user(
        region_id: int, 
        nickname: str, 
        limit: int = 10, 
        check: bool = False
    ) -> ResponseDict:
        try:
            result = await BasicAPI.get_user_search(region_id, nickname, limit)
            if result['code'] != 1000:
                return result
            result = process_search_user_data(region_id,nickname,result,limit,check)
            return result
        except Exception as e:
            raise e

    @ExceptionLogger.handle_program_exception_async
    async def search_clan(
        region_id: int, 
        tag: str, 
        limit: int = 10, 
        check: bool = False
    ) -> ResponseDict:
        try:
            result = await BasicAPI.get_clan_search(region_id, tag, limit)
            if result['code'] != 1000:
                return result
            result = process_search_clan_data(region_id,tag,result,limit,check)
            return result
        except Exception as e:
            raise e
        
    @ExceptionLogger.handle_program_exception_async
    async def search_ship(region_id: int, ship_name: str, language: str, use_nick: bool) -> ResponseDict:
        try:
            data = ShipName.search_ship(ship_name,region_id,language,use_nick)
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e