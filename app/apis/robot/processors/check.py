from app.response import ResponseDict, JSONResponse
from app.const import ClanColor

def process_check_user_data(
    region_id: int, 
    account_id: int, 
    response: dict
) -> ResponseDict:
    # 用户数据
    data = {
        'name': None,
        'hidden': None,
        'level': None,
        'dog_tag': None
    }
    # 处理用户信息
    data['name'] = response['data'][str(account_id)]['name']
    if 'hidden_profile' in response['data'][str(account_id)]:
        data['hidden'] = True
    else:
        data['hidden'] = False
        data['dog_tag'] = response['data'][str(account_id)]['dog_tag']
        if (
            'basic' in response['data'][str(account_id)]
        ):
            data['level'] = response['data'][str(account_id)]['basic']['level']
    return JSONResponse.get_success_response(data)