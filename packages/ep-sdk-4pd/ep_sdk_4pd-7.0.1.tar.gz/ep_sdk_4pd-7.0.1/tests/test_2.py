import time

import requests


def get_history_data(system_date, gap_days, scope="plant,market"):
    url = 'http://82.157.231.254/ep/api/sdk/download_history_data'
    # 
    jdata = {
        "scope": scope,
        "system_date": system_date,
        "days": gap_days,
        "strategy_id": 8
    }
    t0 = time.time()
    res = requests.post(url, json=jdata)
    # 
    res = res.json()
    return res

def train():
    data = get_history_data("2025-07-21", gap_days=567, scope="plant,market,history_predict,history_date_level")

    bikaibiting = data.get("history_date_level")["history_dd_dayahead_opendownunit"]

    print(bikaibiting)

if __name__ == '__main__':
    train()