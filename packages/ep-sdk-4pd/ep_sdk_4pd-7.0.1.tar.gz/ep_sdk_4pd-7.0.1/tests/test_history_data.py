import datetime
from turtle import pd

from ep_sdk_4pd.ep_data import EpData
from ep_sdk_4pd.ep_system import EpSystem


def test_history_data():
    print('-------------test_history_data-------------')

    system_data = EpSystem.get_system_date()
    dt1 = datetime.datetime.strptime("2024-01-01", "%Y-%m-%d")
    dt2 = datetime.datetime.strptime("2025-05-31", "%Y-%m-%d")
    gaps = dt2 - dt1
    gap_days = gaps.days
    print("gap_days:", gap_days)

    data = EpData.init_env('outer').get_history_data(scope="history_date_level", days=3, is_test=True)
    bikaibiting = data.get("history_date_level")["history_dd_dayahead_opendownunit"]
    print(bikaibiting)
    print('-------------------------------------')


if __name__ == '__main__':
    test_history_data()
