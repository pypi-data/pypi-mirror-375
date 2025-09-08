from ep_sdk_4pd.ep_system import EpSystem
from ep_sdk_4pd.ep_data import EpData
import numpy as np
import pandas as pd


def train():
    EpSystem.call_train_done()


def initialize():
    return


def predict():
    target_date = EpSystem.get_system_date()  # 应该需要增加一天表示预测第二天
    plant_forecast_power = EpData.get_predict_data(scope="plant")
    plant_forecast = [float(item['predicted_power']) for item in plant_forecast_power['plant']]

    market_history_data = EpData.get_history_data(scope="market", days=30)
    df_market = pd.DataFrame(market_history_data['market'])
    # Add datetime and hour columns if not already present
    if 'hour' not in df_market.columns:
        df_market['datetime'] = pd.to_datetime(df_market['timestamp'])
        df_market['hour'] = df_market['datetime'].dt.hour

    # Compute proportion where day_ahead_price > electricity_price for each hour
    result = df_market.groupby('hour').apply(
        lambda g: (g['day_ahead_price'] > g['electricity_price']).mean()
    ).reset_index(name='proportion')

    # Find hours where the proportion is greater than 0.5
    hours_with_high_proportion = result[result['proportion'] > 0.5]['hour'].tolist()

    print(f"hours to explode = {hours_with_high_proportion}")

    noon = [4 * hour + i for hour in [9, 10, 11, 12, 13, 14, 15, 16] for i in range(4)]
    inflation_index = [4 * hour + i for hour in hours_with_high_proportion for i in range(4)]
    baoliang_pred = [
        value * 1.4 if index in inflation_index else value
        for index, value in enumerate(plant_forecast)
    ]
    baoliang_pred = np.array(baoliang_pred)
    baoliang_pred = np.maximum(np.minimum(50, baoliang_pred), 0)
    return list(baoliang_pred)
