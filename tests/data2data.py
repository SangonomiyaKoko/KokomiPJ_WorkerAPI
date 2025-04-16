import json
import time

# 原始 JSON 文件路径
input_file = r"F:\Kokomi_PJ_WorkerAPI\temp\json\main.json"
# 输出 JSON 文件路径
output_file = r"F:\Kokomi_PJ_WorkerAPI\temp\json\ship_data1.json"

# 读取原始 JSON 数据
with open(input_file, "r", encoding="utf-8") as f:
    input_data = json.load(f)

result = {
    "update_time": int(time.time()),
    "ship_data": {}
}

region_dict = {
    '1': 'asia',
    '2': 'eu',
    '3': 'na',
    '4': 'ru',
    '5': 'cn'
}

for ship_id, ship_data in input_data.items():
    result["ship_data"][ship_id] = {
        'asia': {},
        'eu': {},
        'na': {},
        'ru': {},
        'cn': {}
    }
    for region_id, region_data in ship_data['region'].items():
        region_str = region_dict.get(region_id)
        data = region_data
        if data == {}:
            continue
        # 原始 battles_count
        battles = data["battles_count"]
        if battles >= 1000:
            # 转换为目标格式
            converted = {
                "battles_count": battles,
                "win_rate": round(data["wins"] * 100, 2),
                "avg_damage": round(data["damage_dealt"], 2),
                "avg_frags": round(data["frags"], 2),
                "avg_exp": round(data["exp"], 2),
                "survived_rate": round(data["survived"], 2),
                "avg_scouting_damage": round(data["scouting_damage"], 2),
                "avg_art_agro": round(data["art_agro"], 2),
                "avg_planes_killed": round(data["planes_killed"], 2),
            }
            result["ship_data"][ship_id][region_str] = converted

# 保存为新的 JSON 文件
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"转换完成，结果已保存到 {output_file}")
