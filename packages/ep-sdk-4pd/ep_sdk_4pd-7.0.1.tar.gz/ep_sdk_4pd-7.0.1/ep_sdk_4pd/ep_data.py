import json
import os
import time
from datetime import timedelta, datetime

import requests

from ep_sdk_4pd import models as ep_sdk_4pd_models
from ep_sdk_4pd.ep_system import EpSystem
from ep_sdk_4pd.models import HistoryDataRequest, PredictDataRequest

# test 地址
# endpoint_inner = 'http://172.27.88.56:5678'

# prod 地址
# endpoint = 'http://ep.4pd.io'

# 外网 地址
endpoint_outer = 'http://ep.4paradigm.com'

# 内网 地址
endpoint_inner = 'http://172.21.80.136'

Authorization = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlbGVjdHJpY2l0eS1wbGF0Zm9ybSIsInN1YiI6IjEyMyIsImlhdCI6MTc0NjYwNjQ4NSwianRpIjoiMTIzXzE3NDY1Nzc2ODUxNDYiLCJ0eXBlIjoiYWNjZXNzIn0.Clrz_8j3aJlXTWPX-4DS0NxXN9idTcUIc0AtXOMIjd8'


class EpData:
    _current_endpoint = endpoint_inner  # 默认内网

    @classmethod
    def init_env(cls, env_type="inner"):
        """设置 API 访问环境
        Args:
            env_type (str):
                'inner' -> 内部环境 http://ep.4pd.io
                'outer' -> 外部环境 http://ep.4paradigm.com
        """
        if env_type == "inner":
            cls._current_endpoint = endpoint_inner
        elif env_type == "outer":
            cls._current_endpoint = endpoint_outer
        else:
            raise ValueError(f"Invalid environment type: {env_type}")
        return cls

    @classmethod
    def get_history_data(
            cls,
            scope="weather,plant,market",
            days=0,
            is_test=False,
            unit_name: str = '达木河二期'
    ):
        # 最晚时间为系统时间 D-2
        date_str = EpSystem.get_system_date(is_online=True)
        calculated_date = datetime.strptime(date_str, "%Y-%m-%d")
        system_date = calculated_date.strftime("%Y-%m-%d")  # 转换回字符串

        if is_test:
            strategy_id = 3
        else:
            strategy_id = os.getenv('STRATEGY_ID')

        request = HistoryDataRequest(
            scope=scope,
            system_date=system_date,
            days=days,
            strategy_id=int(strategy_id),
            unit_name=unit_name
        )
        response = cls.history_data(request=request)

        if response.code == 200:
            return response.data
        else:
            return None

    @classmethod
    def history_data(
            cls,
            request: ep_sdk_4pd_models.HistoryDataRequest = None,
    ) -> ep_sdk_4pd_models.HistoryDataResponse:

        endpoint = cls._current_endpoint
        full_url = f'{endpoint}{request.api}'
        headers = {
            'content-type': request.content_type,
            'Authorization': Authorization
        }
        scopes = request.scope.split(",")
        assert len(scopes) > 0 or "scope 参数错误"
        gfs_resp = None
        if 'gfs' in scopes:
            gfs_resp = EpData.history_large_gfs_data(request=request)
            if gfs_resp.code != 200:
                return gfs_resp
            scopes.remove('gfs')
        if len(scopes) == 0:
            return gfs_resp
        payload = {
            'scope': ",".join(scopes),
            'system_date': request.system_date,
            'days': request.days,
            'strategy_id': request.strategy_id,
            'unit_name': request.unit_name
        }
        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )
        code = response.json().get('code', None)
        data = response.json().get('data', None)
        message = response.json().get('message', None)
        if code == 200 and gfs_resp:
            data.update(gfs_resp.data)
        return ep_sdk_4pd_models.HistoryDataResponse(response=ep_sdk_4pd_models.BaseResponse(**{
            'code': code,
            'data': data,
            'message': message
        }))

    @classmethod
    def history_large_gfs_data(
            cls,
            request: ep_sdk_4pd_models.HistoryDataRequest = None,
    ) -> ep_sdk_4pd_models.HistoryDataResponse:
        """
        由于 gfs 数据可能会比较长，这里处理一下 将长时间的数据进行切分 然后进行组装。
        如果 request.days > 31 那么就将时间按照 31天的时间长度 进行切分
        """
        endpoint = cls._current_endpoint

        unit = 31
        full_url = f'{endpoint}{request.api}'
        headers = {
            'content-type': request.content_type,
            'Authorization': Authorization
        }
        ret = list()
        code = 200
        data = None
        message = None
        days = request.days
        date = datetime.strptime(request.system_date, "%Y-%m-%d")
        while True:
            if days > unit:
                days -= unit
                d = unit
            else:
                d = days
                days = 0

            for _ in range(0, 3):
                payload = {
                    'scope': "gfs",
                    'system_date': date.strftime("%Y-%m-%d"),
                    'days': d,
                    'strategy_id': request.strategy_id
                }
                response = requests.request(
                    method=request.method,
                    url=full_url,
                    headers=headers,
                    data=json.dumps(payload),
                )
                code = response.json().get('code', None)
                data = response.json().get('data', None)
                message = response.json().get('message', None)
                if code == 200:
                    date -= timedelta(days=unit)
                    ret.extend(data['gfs'])
                    break
                else:
                    time.sleep(0.1)
            else:
                return ep_sdk_4pd_models.HistoryDataResponse(response=ep_sdk_4pd_models.BaseResponse(
                    code=code,
                    data=data,
                    message=message,
                ))
            if days == 0:
                break
        base_resp = ep_sdk_4pd_models.BaseResponse(
            code=code,
            data={
                "gfs": ret
            },
            message=message,
        )
        return ep_sdk_4pd_models.HistoryDataResponse(response=base_resp)

    @classmethod
    def get_predict_data(
            cls,
            scope="weather,plant,market",
            is_test=False,
            test_time=None,
            unit_name: str='达木河二期'
    ):
        date_str = EpSystem.get_system_date(is_online=True)
        calculated_date = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)  # 增加 +1 天
        system_date = calculated_date.strftime("%Y-%m-%d")

        # 测试
        if is_test:
            strategy_id = 3
        else:
            strategy_id = os.getenv('STRATEGY_ID')

        request = PredictDataRequest(
            scope=scope,
            system_date=system_date,
            strategy_id=int(strategy_id),
            unit_name=unit_name
        )
        response = cls.predict_data(request=request)

        if response.code == 200:
            return response.data
        else:
            return None

    @classmethod
    def predict_data(
            cls,
            request: ep_sdk_4pd_models.PredictDataRequest = None,
    ) -> ep_sdk_4pd_models.PredictDataResponse:

        endpoint = cls._current_endpoint
        full_url = f'{endpoint}{request.api}'
        headers = {
            'content-type': request.content_type,
            'Authorization': Authorization
        }

        payload = {
            'scope': request.scope,
            'system_date': request.system_date,
            'strategy_id': request.strategy_id,
            'unit_name': request.unit_name
        }

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )

        base_resp = ep_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )
        return ep_sdk_4pd_models.PredictDataResponse(response=base_resp)
