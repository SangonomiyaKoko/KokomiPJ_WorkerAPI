from app.response import ResponseDict, JSONResponse
from app.const import ClanColor

def process_check_user_data(
    region_id: int, 
    account_id: int, 
    response: dict
) -> ResponseDict:
    # 用户数据
    if 'hidden_profile' in response['data'][str(account_id)]:
        hidden = True
    else:
        hidden = False
    # 处理用户信息
    nickname = response['data'][str(account_id)]['name']
    data = {
        'name': nickname,
        'hidden': hidden
    }
    return JSONResponse.get_success_response(data)