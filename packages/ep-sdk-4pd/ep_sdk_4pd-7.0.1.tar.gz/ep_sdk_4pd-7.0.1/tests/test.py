import datetime
import pickle
import requests
import os

import lightgbm as lgb
import numpy as np
import pandas as pd
import holidays
import tempfile
#
#
from ep_sdk_4pd.ep_system import EpSystem
from ep_sdk_4pd.ep_data import EpData


#


def simple_reg_price_step(train, train_label, times=1, cate_fea=[], lr=0.3, steps=500):
    EARLY_STOP_ROUNDS = 50
    #
    # lr = 0.3
    #
    model_list = []
    #
    for i in range(times):
        dtrain = lgb.Dataset(train, train_label, categorical_feature=cate_fea, free_raw_data=False)
        # dval   = lgb.Dataset(test,test_label, categorical_feature=cate_fea,reference = dtrain,free_raw_data=False)
        #
        params = {
            # "min_data_in_bin": 5,
            #
            'num_leaves': 5,
            'min_data_in_leaf': 40,
            'objective': 'regression',
            'max_depth': 4,
            'learning_rate': lr,
            "boosting": "gbdt",
            "feature_fraction": 0.4,
            "bagging_fraction": 0.2,
            "bagging_freq": 1,
            "bagging_seed": 1,
            "metric": 'mse',
            "lambda_l1": 0.01,
            "lambda_l2": 0.01,
            "random_state": 1022 + i,
            "num_threads": -1,
            'verbose': 1,
            #
            'early_stopping_round': EARLY_STOP_ROUNDS,
            'verbose_eval': 10,
        }
        model = lgb.train(
            params,
            dtrain,
            num_boost_round=steps,
            # feval=calc_wauc,
            valid_sets=[dtrain],
            # verbose_eval=10,
            # early_stopping_rounds=EARLY_STOP_ROUNDS
        )
        model_list.append(model)
    #
    # meta_prob = None
    # meta_prob = np.zeros(len(test_label))
    # for m in model_list:
    #     meta_prob += m.predict(test)
    # meta_prob /= len(model_list)

    return model_list[0]


#


def get_data_label(market, power, weather=None, istrain=True):
    #
    #
    float_names = ["win_out", "sun_out", "tongdiao", "lianluo"] \
                  + ["bwin_out", "bsun_out", "btongdiao", "blianluo"] \
                  + ["bshui_huo", "shui_huo"] \
                  + ["real_fact_price", "before_fact_price"] \
                  + ["idx"] \
                  + ["power_pred"] \
        #
    wnames = [col for col in weather.columns if
              col not in ["time_point", "ref_date", "gfs_time"]] if weather is not None else []
    weather = [row for idx, row in weather.iterrows()] if weather is not None else []
    #
    float_names = float_names + wnames
    #
    #
    price_names = ["before_price", "real_price", "diff_price", "diff_pos"] if istrain else []
    #
    all_datas = {
        name: [] for name in ["datetime"] + float_names + price_names
        #
    }
    #
    market = sorted(market, key=lambda x: x["timestamp"], reverse=False)
    power = sorted(power, key=lambda x: x["timestamp"], reverse=False)
    # market = sorted(market, key=lambda x: [-int(x["datetime"].split("-")[0]), x["datetime"].split("-")[1]])
    #
    # power_pred = power["predicted_power"].tolist()
    power_pred = [p["predicted_power"] for p in power]
    #
    #
    for idx, row in enumerate(power):
        if istrain:
            if idx < 96 * 2:
                continue
        #
        sup_now = market[idx] if idx < len(market) else None
        if sup_now is None:
            print(f"Warning: Missing market data at index {idx}")
            continue
        sup_before = market[idx]
        if istrain:
            sup_before = market[idx - 96 * 2]
        #
        time_str = str(row['timestamp']).strip()
        #
        print(f"sup_before timestamp: {sup_before['timestamp']}")
        #
        date_part, time_part = time_str.split(' ')
        if time_part == '24:00:00':
            day = datetime.datetime.strptime(date_part, '%Y-%m-%d') + datetime.timedelta(days=1)
            day = day.replace(hour=0, minute=0, second=0)
        else:
            day = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        #
        day_now = datetime.datetime.strftime(day, '%Y-%m-%d %H:%M:%S')
        all_datas["datetime"].append(day_now)
        #
        #
        #
        all_datas["bwin_out"].append(sup_before['wind_power_day_ahead'])
        all_datas["bsun_out"].append(sup_before['pv_power_day_ahead'])
        all_datas["btongdiao"].append(sup_before['provincial_load_forecast'])
        all_datas["blianluo"].append(-sup_before['day_ahead_tieline_power'])
        all_datas["bshui_huo"].append(
            sup_before['provincial_load_forecast'] - sup_before['day_ahead_tieline_power'] - sup_before[
                'pv_power_day_ahead'] - sup_before['wind_power_day_ahead'])
        #
        #
        all_datas["win_out"].append(sup_before['wind_power_actual_value'])
        all_datas["sun_out"].append(sup_before['pv_actual_value'])
        all_datas["tongdiao"].append(sup_before['system_load_actual_value'])
        all_datas["lianluo"].append(-sup_before['tie_line_out_actual_value'])
        all_datas["shui_huo"].append(
            sup_before['system_load_actual_value'] - sup_before['tie_line_out_actual_value'] - sup_before[
                'pv_actual_value'] - sup_before['wind_power_actual_value'])
        #
        all_datas["before_fact_price"].append(sup_before['day_ahead_price'])
        all_datas["real_fact_price"].append(sup_before['electricity_price'])
        all_datas["idx"].append(idx % 96)
        all_datas["power_pred"].append(power_pred[idx])
        # #
        #
        #
        for key in wnames:
            all_datas[key].append(weather[idx][key])
        #
        if istrain:
            all_datas["before_price"].append(sup_now['day_ahead_price'])
            all_datas["real_price"].append(sup_now['electricity_price'])
            all_datas["diff_price"].append(sup_now['day_ahead_price'] - sup_now['electricity_price'])
            all_datas["diff_pos"].append(1 if sup_now['day_ahead_price'] - sup_now['electricity_price'] > 0 else 0)
    #
    #
    float_names = [name for name in float_names if name not in []]
    # float_names = [name for name in float_names if name not in ["power_pred"]]
    #
    all_datas = pd.DataFrame(all_datas)
    return all_datas, float_names


#


def train():
    #
    cn_holidays = holidays.CountryHoliday('CN')
    #
    # system_date = EpSystem.get_system_date()  # 输出 eg:2025-01-01
    system_date = datetime.datetime(
        year=2025,
        month=4,
        day=12
    ).strftime("%Y-%m-%d")
    dt1 = datetime.datetime.strptime("2024-01-01", "%Y-%m-%d")
    dt2 = datetime.datetime.strptime(system_date, "%Y-%m-%d")
    dt3 = datetime.datetime.strptime('2025-01-01', "%Y-%m-%d")
    gaps = dt2 - dt1
    gap_days = gaps.days
    #
    print(f"system_date: {system_date}")
    print(f"gap_days: {gap_days}")
    #
    # gap_days = 1000
    #
    # system_date - 1: 所有字段
    data = EpData.get_history_data(scope="weather,plant,market", days=gap_days)
    # data = EpData.get_history_data(scope=["weather","plant","market"], days=gap_days)
    #
    #
    gaps = dt3 - dt1
    gap_days = gaps.days
    examples = gap_days * 96
    #
    weather = data.get("weather")
    plant = data.get("plant")[:examples]
    market = data.get("market")[:examples]
    #
    # weather = data["weather"]
    # plant = data["plant"]
    # market = data["market"]
    #
    #
    all_datas, float_names = get_data_label(market, plant, weather=None, istrain=True)
    #
    #
    all_datas["datetime"] = all_datas["datetime"].apply(
        lambda x: datetime.datetime.strptime(str(x).strip(), '%Y-%m-%d %H:%M:%S'))
    #
    all_datas["weekday"] = all_datas["datetime"].apply(lambda x: x.weekday())
    all_datas["hour"] = all_datas["datetime"].apply(lambda x: x.hour)
    all_datas["month"] = all_datas["datetime"].apply(lambda x: x.month)
    all_datas["holiday"] = all_datas["datetime"].apply(lambda x: 1 if x.date() in cn_holidays else 0)
    #
    #
    cate_names = ["weekday", "hour", "month", "holiday"]
    print(f"cate_names: {cate_names}")
    #
    #
    for name in cate_names:
        all_datas[name] = all_datas[name].astype('category')
    for name in float_names:
        all_datas[name] = all_datas[name].astype(float)
    #
    #
    #
    target = "before_price"  # before_price, real_price, diff_price
    X_train, y_train = all_datas[float_names + cate_names], all_datas[target]
    model_before = simple_reg_price_step(X_train, y_train, 1, cate_fea=cate_names, lr=0.15, steps=73)
    #
    target = "real_price"  # before_price, real_price, diff_price
    X_train, y_train = all_datas[float_names + cate_names], all_datas[target]
    model_real = simple_reg_price_step(X_train, y_train, 1, cate_fea=cate_names, lr=0.05, steps=192)
    #
    #
    reqian_res = {}
    reqian_res['model_before'] = model_before
    reqian_res['float_names'] = float_names
    reqian_res['cate_names'] = cate_names
    reqian_res['model_real'] = model_real
    #
    # shishi_res = {}
    # shishi_res['float_names'] = float_names
    # shishi_res['cate_names'] = cate_names
    #
    base = "./tmp"
    if not os.path.exists(base):
        os.makedirs(base)
    #
    with open(f'{base}/riqian_price.pickle', 'wb') as handle:
        pickle.dump(reqian_res, handle)
    # with open(f'{EpSystem.model_output_dir()}/shishi_price.pickle', 'wb') as handle:
    #     pickle.dump(shishi_res, handle)
    #
    #
    EpSystem.call_train_done()


#


#
#
inited = False
riqian_model = None
riqian_cate = None
riqian_float = None
shishi_model = None
cn_holidays = holidays.CountryHoliday('CN')


def initialize():
    global inited, riqian_model, riqian_cate, riqian_float, shishi_model
    #
    #
    #
    base = "./tmp"
    path = f'{base}/riqian_price.pickle'
    #
    # url = f'{EpSystem.model_output_dir()}/riqian_price.pickle'
    # response = requests.get(url)
    # response.raise_for_status()
    # #
    # with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #     tmp_file.write(response.content)
    #     path = tmp_file.name
    #
    with open(path, 'rb') as f:
        # riqian_res = pickle.load(f)ode-file/20250522041137_submit_0521.py/riqian_price.pickle'
        #
        riqian_res = pickle.load(f)
        riqian_model = riqian_res["model_before"]
        riqian_cate = riqian_res["cate_names"]
        riqian_float = riqian_res["float_names"]
        shishi_model = riqian_res["model_real"]
    #
    #
    inited = True
    #


#


def get_baoliang(riqian_pred, shishi_pred, power_pred):
    #
    min_report, max_report, step = 0, 50, 0.1

    #
    def get_factor(diff1, diff2, p_power):
        # [0, 1000] -> [1, 0.1]
        #
        maxv = 250
        diff1 = min(diff1, maxv)
        factor1 = ((maxv - diff1) / maxv) ** 2 + 0.00
        #
        rate = min(diff2 / (0.4 * max(p_power, 0.1)), 3) + 0.00
        #
        return factor1 * rate

    #
    punish = 0.22

    def get_profit(baoliang, r_price, s_price, p_power, bad_point):
        #
        risk = 0
        profit_factor = (baoliang - p_power) * (r_price - s_price)
        #
        #
        punish_factor = punish
        #
        if bad_point:
            punish_factor = punish_factor * 100
        #
        normal = abs(baoliang - p_power) / (max_report - p_power) if baoliang > p_power else (
            abs(baoliang - p_power) / p_power if p_power != 0 else 0)
        #
        if profit_factor > 0:
            profit_factor = min(abs(baoliang - p_power), 0.4 * p_power) * abs(r_price - s_price)
            factor = get_factor(abs(r_price - s_price), abs(baoliang - p_power), p_power)
            risk = punish_factor * abs(baoliang - p_power) * abs(r_price - s_price) * factor
            #
        profit_withdraw = profit_factor + p_power * r_price
        #
        #
        return profit_withdraw - risk
        # return baoliang * r_price + (p_power - baoliang) * s_price - punish * normal * abs(baoliang - p_power) * abs(r_price - s_price)

    #
    #
    day_point = 96
    baoliang_profit_map = []
    #
    for idx, (r_pred, s_pred, p_pred) in enumerate(zip(riqian_pred, shishi_pred, power_pred)):
        #
        # fadian = p_pred
        # fadian = p_pred + 1.5
        fadian = p_pred + 3.5
        #
        bad_point = idx < 6 * 4 or idx > 22 * 4
        #
        except_profits = []
        baoliang = min_report
        #
        while baoliang < max_report:
            profit = get_profit(baoliang, r_pred, s_pred, fadian, bad_point)
            except_profits.append(profit)
            #
            baoliang += step
        baoliang_profit_map.append(except_profits)
        #
    #
    # order1_max = 4.5
    order1_max = 3.7
    # order1_max = 3
    #
    range_skip = int(order1_max / step)
    #
    #
    posi_num = int(max_report / step)
    #
    start = 0
    pre_best = [[i for i in range(posi_num)]]
    for point in range(start + 1, start + day_point):
        best_pre = []
        for idx in range(posi_num):
            min_pos, max_pos = max(0, idx - range_skip), min(posi_num - 1, idx + range_skip)
            index = np.argmax(baoliang_profit_map[point - 1][min_pos:max_pos]) + min_pos
            baoliang_profit_map[point][idx] += baoliang_profit_map[point - 1][index]
            best_pre.append(index)
        pre_best.append(best_pre)
    #
    last_max = np.argmax(baoliang_profit_map[start + day_point - 1])
    #
    pre_list = [last_max]
    for idx in range(len(pre_best) - 1, 0, -1):
        last_max = pre_best[idx][last_max]
        pre_list.append(last_max)
    pre_list.reverse()
    #
    baoliangs = [v * step for v in pre_list]
    #
    return baoliangs


#

def predict():
    global cn_holidays, inited, riqian_model, riqian_cate, riqian_float, shishi_model
    #
    if not inited:
        initialize()
    #
    #
    target_date = EpSystem.get_system_date()
    #
    # system_date + 1: plant/weather
    data = EpData.get_predict_data(scope="plant,weather")
    # data = EpData.get_predict_data(scope=["plant","weather"])
    #
    #
    if data is None or len(data) == 0:
        return None
    plant = data["plant"]
    weather = data["weather"]
    #
    # system_date - 1: market
    data = EpData.get_history_data(scope="market", days=1)
    # data = EpData.get_history_data(scope=["market"], date=1)
    market = data["market"]
    #
    #
    price_data, float_names = get_data_label(market, plant, weather=None, istrain=False)
    #
    price_data = price_data.tail(96)
    #
    #
    #
    price_data["datetime"] = price_data["datetime"].apply(
        lambda x: datetime.datetime.strptime(str(x).strip(), '%Y-%m-%d %H:%M:%S'))
    #
    price_data["weekday"] = price_data["datetime"].apply(lambda x: x.weekday())
    price_data["hour"] = price_data["datetime"].apply(lambda x: x.hour)
    price_data["month"] = price_data["datetime"].apply(lambda x: x.month)
    price_data["holiday"] = price_data["datetime"].apply(lambda x: 1 if x.date() in cn_holidays else 0)
    #
    #
    for col in riqian_cate:
        price_data[col] = price_data[col].astype('category')
    for col in riqian_float:
        price_data[col] = price_data[col].astype('float')
    #
    #
    riqian_test = price_data[riqian_model.feature_name()]
    riqian_pred = list(riqian_model.predict(riqian_test))
    #
    shishi_test = price_data[shishi_model.feature_name()]
    shishi_pred = list(shishi_model.predict(shishi_test))
    #
    # fadianpred = [v1 + v2 for v1, v2 in zip(fadianpred, price_data["power_pred"].tolist())]
    fadianpred = [40.96, 40.96, 40.96, 72.62, 33.18, 72.62, 33.18, 72.62, 33.18, 72.66, 33.05, 72.66, 33.05, 72.66, 33.05, 40.7, 40.7, 40.7, 72.76, 32.93, 40.52, 40.52, 40.52, 72.76, 32.93, 72.76, 32.93, 40.38, 40.38, 72.95, 32.76, 72.95, 32.76, 72.95, 32.76, 40.38, 73.21, 32.47, 73.21, 32.47, 73.21, 32.47, 40.29, 40.29, 40.29, 40.19, 40.19, 40.19, 73.47, 32.37, 73.47, 32.37, 73.47, 32.37, 40.04, 73.74, 32.32, 73.74, 32.32, 73.74, 32.32, 40.04, 40.04, 73.91, 32.34, 73.91, 32.34, 39.93, 39.93, 39.93, 73.91, 32.34, 39.8, 39.8, 39.8, 73.99, 32.38, 73.99, 32.38, 73.99, 32.38, 74.1, 32.44, 74.1, 32.44, 74.1, 32.44, 39.67, 39.67, 39.67, 74.2, 32.48, 39.58, 39.58, 39.58, 74.2]
    #
    baoliangs = get_baoliang(riqian_pred, shishi_pred, fadianpred)
    #
    center = 13 * 4
    baoliangs = [
        val * (abs(idx - center) ** 4 / 40000 + 0.45) if idx >= 10 * 4 and idx <= 16 * 4 else val for idx, val in
        enumerate(baoliangs)
    ]
    baoliangs = [f"{val:.2f}" for val in baoliangs]
    #
    print(f'target_date={target_date},riqian_pred={riqian_pred},  shishi_pred={shishi_pred}, fadianpred={fadianpred}')
#


if __name__ == '__main__':
    train()

    initialize()

    predict()