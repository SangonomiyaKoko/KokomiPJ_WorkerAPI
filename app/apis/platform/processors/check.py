from app.response import ResponseDict, JSONResponse
from app.const import ClanColor

def process_check_user_data(
    region_id: int, 
    account_id: int, 
    response: dict
) -> ResponseDict:
    # 用户数据
    if response['code'] == 1001:
        return JSONResponse.API_1001_UserNotExist
    # 处理用户信息
    nickname = response['data'][str(account_id)]['name']
    data = {
        'account_id': account_id,
        'region_id': region_id,
        'name': nickname
    }
    return JSONResponse.get_success_response(data)