from ep_sdk_4pd.ep_data import EpData


def test_predict_data():
    print('-------------test_predict_data-------------')

    data = EpData.init_env("outer").get_predict_data(scope="market", is_test=True)
    print(data)
    print('-------------------------------------')


if __name__ == '__main__':
    test_predict_data()
