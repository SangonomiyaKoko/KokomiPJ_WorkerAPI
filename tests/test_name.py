import jellyfish
import json
import operator

# 示例数据（你可以从文件中加载完整数据）
ship_data = {
    "3765319664": {
        "tier": 5,
        "type": "Destroyer",
        "nation": "usa",
        "premium": True,
        "special": False,
        "index": "PASD505",
        "ship_name": {
            "cn": "希尔",
            "en": "Hill",
            "en_l": "Hill",
            "ja": "Hill",
            "ru": "Hill"
        }
    },
    "1234567890": {
        "tier": 10,
        "type": "Battleship",
        "nation": "jpn",
        "premium": False,
        "special": False,
        "index": "PJSD110",
        "ship_name": {
            "cn": "大和",
            "en": "Yamato",
            "en_l": "Battleship Yamato",
            "ja": "大和",
            "ru": "Ямато"
        }
    }
}

# 匹配优先级映射
fallback_map = {
    "cn": ["cn", "en"],
    "ja": ["ja", "en"],
    "ru": ["ru", "en"],
    "en": ["en", "en_"]
}

def normalize(text: str) -> str:
    return text.lower().strip()

def fuzzy_match(user_input: str, lang: str, ships: dict, top_n: int = 5):
    user_input_norm = normalize(user_input)
    candidates = []

    # 决定匹配的字段列表
    lang_priority = fallback_map.get(lang, ["en"])

    for ship_id, info in ships.items():
        names = info["ship_name"]
        for lang_key in lang_priority:
            name = names.get(lang_key)
            if name:
                name_norm = normalize(name)
                score = jellyfish.jaro_winkler_similarity(user_input_norm, name_norm)
                if score > 0.3:  # 设置一个合理的匹配阈值
                    candidates.append({
                        "ship_id": ship_id,
                        "match_name": name,
                        "match_lang": lang_key,
                        "score": score,
                        "index": info.get("index")
                    })
                break  # 匹配成功一个语言就不继续 fallback

    # 按匹配度排序
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_n]

# === 示例测试 ===
if __name__ == "__main__":
    test_cases = [
        {"input": "希尓", "lang": "cn"},
        {"input": "yamato", "lang": "en"},
        {"input": "Ямото", "lang": "ru"},
        {"input": "やまと", "lang": "ja"},
    ]

    for case in test_cases:
        print(f"\n[输入: {case['input']} | 语言: {case['lang']}]")
        results = fuzzy_match(case["input"], case["lang"], ship_data)
        for r in results:
            print(f"  -> 匹配舰船: {r['match_name']} | 相似度: {r['score']:.3f} | index: {r['index']}")
