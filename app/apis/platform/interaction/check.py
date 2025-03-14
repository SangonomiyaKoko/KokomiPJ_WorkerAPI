from app.network import BasicAPI
from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.utils import ShipName
from ..processors.check import (
    process_check_user_data,
)


class CheckID:
    @ExceptionLogger.handle_program_exception_async
    async def check_user(
        region_id: int, 
        account_id: int
    ) -> ResponseDict:
        try:
            result = await BasicAPI.get_user_basic(account_id, region_id)
            if result[0]['code'] != 1000:
                return result[0]
            result = process_check_user_data(region_id,account_id,result[0])
            return result
        except Exception as e:
            raise e