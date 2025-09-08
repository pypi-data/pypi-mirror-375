# -*- coding: UTF-8 -*-
# @Time : 2024/8/14 23:58 
# @Author : 刘洪波
import hashlib
import base64
import random
import requests
import json
import aiohttp
from datetime import datetime
from bigtools import ContentType


def insert_middle(str1, str2):
    length = min(len(str1), len(str2))
    result = [str1[i] + str2[i] for i in range(length)]
    result.append(str1[length:])
    result.append(str2[length:])
    return ''.join(result)


def insert_front(str1, str2): return str2 + str1


def insert_after(str1, str2): return str1 + str2


merge_algorithm_dict = {
    'insert_middle': insert_middle,
    'insert_front': insert_front,
    'insert_after': insert_after
}


def merge_str(str1, str2, algorithm: str = 'insert_middle') -> str:
    if str1 and str2 and algorithm:
        if algorithm in merge_algorithm_dict:
            return eval(algorithm)(str1, str2)
        else:
            raise ValueError('Error: The input parameter algorithm is incorrect!')
    else:
        raise ValueError('Error: Input parameter error, please check!')


def generate_sign(key: str, timestamp: str, algorithm: str = None):
    """
    生成sign
    :param key: 生成签名所需密钥
    :param timestamp: 时间戳
    :param algorithm: 生成签名方式
    :return:
    """
    if not algorithm:
        algorithm = random.choice(list(merge_algorithm_dict.keys()))
    _key = merge_str(key, timestamp, algorithm)
    hash_object = hashlib.sha256()
    hash_object.update(_key.encode())
    return algorithm, hash_object.hexdigest()


def generate_fused_sign(key: str, timestamp: str, algorithm: str = None, user_id: str = None):
    """
    生成融合的签名，签名里包含 时间戳 或 用户ID
    :param key: 生成签名所需密钥
    :param timestamp: 时间戳
    :param algorithm: 生成签名方式
    :param user_id: 用户ID
    :return:
    """
    algorithm, sign = generate_sign(key, timestamp, algorithm)
    content = algorithm + '###' + sign + '###' + timestamp
    if user_id:
        content += '###' + user_id
    return base64.b64encode(content.encode()).decode('utf-8')


def parse_sign(sign: str):
    """
    解析签名
    :param sign: 签名
    :return:
    """
    sign_info = {}
    if sign:
        new_sign = base64.b64decode(sign).decode('utf-8')
        if '###' in new_sign:
            new_sign = new_sign.split('###')
            if len(new_sign) > 1:
                sign_info['algorithm'] = new_sign[0]
                sign_info['sign'] = new_sign[1]
            if len(new_sign) > 2:
                sign_info['timestamp'] = new_sign[2]
            if len(new_sign) > 3:
                sign_info['user_id'] = '###'.join(new_sign[3:])
    return sign_info


def verify_easy_sign(sign: str, key: str):
    """验证简单免加密签名"""
    sign_info = {}
    if sign:
        new_sign = base64.b64decode(sign).decode('utf-8')
        if '###' in new_sign:
            new_sign = new_sign.split('###')
            if len(new_sign) == 2:
                sign_info['user_id'] = new_sign[0]
                if new_sign[1] == key:
                    sign_info['authorization'] = True
    return sign_info


def generate_easy_sign(user_id: str, key: str):
    """生成简单免加密签名"""
    if user_id and key:
        if '###' in key:
            raise ValueError('Error: key can not contain "###"')
        return base64.b64encode(f'{user_id}###{key}'.encode()).decode('utf-8')
    else:
        raise ValueError('Error: user_id and key can not be empty')


def generate_fixed_sign(key: str):
    """
    生成加密的固定签名
    时间在整点一小时内生成固定的sign
    例如：1点-2点间sign_1是相同的，2点-3点间sign_2是相同的， sign_1 与sign_2 不同
    """
    if key:
        now = datetime.now()
        now = now.replace(minute=0, second=0, microsecond=0)
        key += str(int(now.timestamp()))
        hash_object = hashlib.sha256()
        hash_object.update(key.encode())
        return hash_object.hexdigest()
    else:
        raise ValueError('Error: key can not be empty')


def generate_fixed_encoded_sign(key: str):
    """对加密的固定签名进行编码"""
    return base64.b64encode(f'Fixed###{generate_fixed_sign(key)}'.encode()).decode('utf-8')


def verify_fixed_encoded_sign(sign: str, key: str):
    """验证编码后的加密的固定签名"""
    sign_info = parse_sign(sign)
    if sign_info['algorithm'] == 'Fixed':
        if sign_info['sign'] == generate_fixed_sign(key):
            return True
    return False


def verify_sign_by_api(sign: str, url: str):
    """通过进行验证"""
    resp = requests.post(url, data=json.dumps({'sign': sign}), headers=ContentType.app_json_headers)
    if resp.status_code == 200:
        resp_json = resp.json()
        if resp_json['code'] == 200:
            return resp_json['data']
    return {}


async def async_verify_sign_by_api(sign: str, url: str):
    """异步通过进行验证"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps({'sign': sign}), headers=ContentType.app_json_headers) as resp:
            status_code = resp.status
            if status_code == 200:
                resp_json = await resp.json()
                if resp_json['code'] == 200:
                    return resp_json['data']
    return {}


def common_verify_sign(input_sign: str, my_sign: str, key: str, url: str):
    """通用验证"""
    if input_sign == my_sign:
        return {'authorization': True, 'type': 'one', 'user_id': ''}
    if verify_fixed_encoded_sign(input_sign, key):
        return {'authorization': True, 'type': 'two', 'user_id': ''}
    if verify_sign_by_api(input_sign, url).get('authorization'):
        return {'authorization': True, 'type': 'three',
                'user_id': verify_sign_by_api(input_sign, url).get('user_id', '')}
    return {'authorization': False, 'type': '', 'user_id': ''}


async def async_common_verify_sign(input_sign: str, my_sign: str, key: str, url: str):
    """异步通用验证"""
    if input_sign == my_sign:
        return {'authorization': True, 'type': 'one', 'user_id': ''}
    if verify_fixed_encoded_sign(input_sign, key):
        return {'authorization': True, 'type': 'two', 'user_id': ''}
    verify_info = await async_verify_sign_by_api(input_sign, url)
    if verify_info.get('authorization'):
        return {'authorization': True, 'type': 'three',
                'user_id': verify_sign_by_api(input_sign, url).get('user_id', '')}
    return {'authorization': False, 'type': '', 'user_id': ''}
