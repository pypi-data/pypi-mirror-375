import base64
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
import rsa

from ep_sdk_4pd import models as ep_sdk_4pd_models
from ep_sdk_4pd.models import RunStrategyRequest, CallTrainDoneRequest, RsaKeyRequest

# test 地址
# endpoint_inner = 'http://172.27.88.56:5678'

# prod 地址
# endpoint = 'http://ep.4pd.io'

# 外网地址
endpoint_outer = 'http://ep.4paradigm.com'

# 内网地址
endpoint_inner = 'http://172.21.80.136'

Authorization = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlbGVjdHJpY2l0eS1wbGF0Zm9ybSIsInN1YiI6IjEyMyIsImlhdCI6MTc0NjYwNjQ4NSwianRpIjoiMTIzXzE3NDY1Nzc2ODUxNDYiLCJ0eXBlIjoiYWNjZXNzIn0.Clrz_8j3aJlXTWPX-4DS0NxXN9idTcUIc0AtXOMIjd8'


def rsa_decrypt(privkey, ciphertext):
    decrypted = rsa.decrypt(base64.b64decode(ciphertext), privkey)
    return decrypted.decode('utf-8')


class EpSystem:
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

    @staticmethod
    def model_output_dir():
        user_home = os.path.expanduser('root')
        base_dir = os.path.join(user_home, "modelResult")

        # 从环境变量中获取策略id
        strategy_id = os.getenv('STRATEGY_ID')
        logging.info(f'strategy_id: {strategy_id}')

        if strategy_id is None:
            raise Exception('STRATEGY_ID is not set')

        target_dir = os.path.join(base_dir, f"{strategy_id}")
        Path(target_dir).mkdir(parents=True, exist_ok=True)

        abs_path = os.path.abspath(target_dir)
        return abs_path

    @classmethod
    def get_system_date(cls, is_online: bool = True):
        """
        脚本每次预测的目标日，主要是拦截用户获取越界数据,用户不可修改
        """
        if is_online:
            # 线上环境,随着真实调用运行时间变化
            system_date = datetime.now().strftime('%Y-%m-%d')

            target_date = os.environ.get('TARGET_DATE')
            if target_date is not None:
                rsa_data = cls.get_rsa_key()
                if rsa_data:
                    rsa_private_key = rsa_data['rsa_private_key']
                    loaded_privkey = rsa.PrivateKey.load_pkcs1(rsa_private_key.encode('utf-8'))
                    decrypted_data = rsa_decrypt(loaded_privkey, target_date)
                    system_date = decrypted_data
        else:
            # 线下环境
            system_date = "2024-12-31"

        return system_date

    @classmethod
    def get_run_strategy(cls, is_online: bool = True):
        """
        获取此刻运行的策略模型基础信息
        :param is_online:
        :return:
        """
        endpoint = cls._current_endpoint
        if is_online:
            # 从环境变量中获取策略id
            strategy_id = os.getenv('STRATEGY_ID')
            logging.info(f'strategy_id: {strategy_id}')

            if strategy_id is None:
                raise Exception('STRATEGY_ID is not set')
        else:
            # 线下环境，给固定的策略id
            strategy_id = 1

        request = RunStrategyRequest(strategy_id=strategy_id)
        full_url = f'{endpoint}{request.api}'
        headers = {
            'content-type': request.content_type,
            'Authorization': Authorization
        }

        payload = {
            'strategy_id': request.strategy_id
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
        response = ep_sdk_4pd_models.RunStrategyResponse(response=base_resp)

        if response.code == 200:
            return response.data
        else:
            return None

    @classmethod
    def call_train_done(
            cls,
            strategy_id: int = None,
            script_strategy_id: int = None
    ):
        endpoint = cls._current_endpoint
        if strategy_id is None or script_strategy_id is None:
            strategy_id = os.getenv('STRATEGY_ID')
            script_strategy_id = os.getenv('SCRIPT_STRATEGY_ID')

        request = CallTrainDoneRequest(
            strategy_id=strategy_id,
            script_strategy_id=script_strategy_id
        )
        full_url = f'{endpoint}{request.api}'
        headers = {
            'content-type': request.content_type,
            'Authorization': Authorization
        }

        payload = {
            'strategy_id': request.strategy_id,
            'script_strategy_id': request.script_strategy_id
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
        response = ep_sdk_4pd_models.CallTrainDoneResponse(response=base_resp)

        if response.code == 200:
            return True
        else:
            return False

    @classmethod
    def get_rsa_key(cls):
        request = RsaKeyRequest()
        response = cls.rsa_key(request=request)

        if response.code == 200:
            return response.data
        else:
            return None

    @classmethod
    def rsa_key(
            cls,
            request: ep_sdk_4pd_models.RsaKeyRequest = None,
    ) -> ep_sdk_4pd_models.RsaKeyResponse:

        endpoint = cls._current_endpoint
        full_url = f'{endpoint}{request.api}'
        headers = {
            'content-type': request.content_type,
            'Authorization': Authorization
        }

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
        )

        base_resp = ep_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )
        return ep_sdk_4pd_models.RsaKeyResponse(response=base_resp)
