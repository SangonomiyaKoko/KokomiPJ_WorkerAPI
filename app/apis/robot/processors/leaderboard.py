def process_leaderboard_page_data(page_data: list):
    result = []
    for index in page_data:
        if index['clan_tag'] != 'nan':
            clan_class, clan_tag = index['clan_tag'].split('|')
        else:
            clan_class, clan_tag = 5, 'nan'
        battle_class, battle_type = index['battle_type'].split('|')
        rating_class, rating_value = index['rating'].split('|')
        win_rate_class, win_rate = index['win_rate'].split('|')
        avg_dmg_class, avg_dmg = index['avg_dmg'].split('|')
        avg_frags_class, avg_frags = index['avg_frags'].split('|')

        index['clan_tag'] = clan_tag
        index['battle_type'] = battle_type
        index['rating'] = rating_value
        index['win_rate'] = win_rate
        index['avg_dmg'] = avg_dmg
        index['avg_frags'] = avg_frags

        index['clan_tag_class'] = int(clan_class)
        index['battle_type_class'] = int(battle_class)
        index['rating_class'] = int(rating_class)
        index['win_rate_class'] = int(win_rate_class)
        index['avg_dmg_class'] = int(avg_dmg_class)
        index['avg_frags_class'] = int(avg_frags_class)

        result.append(index)
    return result

def process_leaderboard_overall_data(user_data: dict):
    result = {
        'battles_count': 0,
        'win_rate': 0.0,
        'avg_damage': 0,
        'avg_frags': 0.0,
        'rating': 0,
        'win_rate_class': 0,
        'avg_damage_class': 0,
        'avg_frags_class': 0,
        'rating_class': 0
    }
    result['battles_count'] = '{:,}'.format(int(user_data['battles_count'])).replace(',', ' ')
    win_rate_class, win_rate = user_data['win_rate'].split('|')
    result['win_rate'] = win_rate
    result['win_rate_class'] = int(win_rate_class)
    avg_dmg_class, avg_dmg = user_data['avg_dmg'].split('|')
    result['avg_damage'] = '{:,}'.format(int(avg_dmg)).replace(',', ' ')
    result['avg_damage_class'] = int(avg_dmg_class)
    avg_frags_class, avg_frags = user_data['avg_frags'].split('|')
    result['avg_frags'] = avg_frags
    result['avg_frags_class'] = int(avg_frags_class)
    rating_class, rating_value = user_data['rating'].split('|')
    result['rating'] = '{:,}'.format(int(rating_value)).replace(',', ' ')
    result['rating_class'] = int(rating_class)

    return result

def process_leaderboard_rank_data(rank_data: dict):
    result = {
        'rank': None,
        'percentage': None,
        'distribution': {
            'user_bin': None,
            'bin_count': None
        }
    }
    result['rank'] = str(rank_data['rank'])
    result['percentage'] = rank_data['percentage']
    result['distribution']['user_bin'] = str(rank_data['distribution']['user_bin'])
    temp_dict = {}
    i = 0
    while i <= 5000:
        temp_dict[str(i)] = 0
        i += 200
    bins = rank_data['distribution']['bins']
    counts = rank_data['distribution']['counts']
    for i in range(len(counts)):
        if bins[i] >= 5000:
            temp_dict['5000'] += counts[i]
        else:
            temp_dict[str(bins[i])] += counts[i]
    result['distribution']['bin_count'] = temp_dict
    return result

