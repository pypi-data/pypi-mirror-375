# -*- coding: UTF-8 -*-
# @Time : 2023/9/27 17:58 
# @Author : 刘洪波
import time
import random
import requests
from requests.adapters import HTTPAdapter
from functools import wraps
from tqdm import tqdm
from bigtools.more_tools import get_file_size
from bigtools.default_data import headers as df_headers


def get_requests_session(max_retries: int = 3):
    """
    使用requests Session，使抓取数据的时候可以重试
    # 默认设置重试次数为3次
    """
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=max_retries))
    session.mount('https://', HTTPAdapter(max_retries=max_retries))
    return session


class DealException(object):
    """处理异常返回的装饰器"""
    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(e)
        return wrapped_function


def save_response_data(response, total: int, file_path: str, initial: int = 0):
    """
    保存响应数据
    :param response: 请求响应
    :param total: 数据大小
    :param file_path: 保存的数据路径
    :param initial: 进度条初始化大小
    :return:
    """
    file_op = 'ab' if initial else 'wb'
    with open(file_path, file_op) as file, tqdm(
        desc=file_path,
        total=total,
        initial=initial,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


# 下载数据
def download(url: str, file_path: str, headers: dict = df_headers, read_timeout: int = 15,
             resume: bool = True, max_retries: int = 3):
    """
    下载流式传输的文件，比如：压缩包、音频、视频等等
    :param url: 文件下载链接
    :param file_path: 文件保存路径
    :param headers: 请求头
    :param read_timeout:
    :param resume: 是否断点续传，默认进行断点续传。值为True进行断点续传；值为False从头开始下载，不进行断点续传。
    :param max_retries: 最大重试次数，网络不好时增大 max_retries
    :return:
    """
    if 'Range' in headers:
        del headers['Range']

    requests_session = get_requests_session(max_retries)

    @DealException()
    def get_data():
        return requests_session.get(url, headers=headers, stream=True, timeout=(read_timeout, 5))

    response = get_data()
    total = int(response.headers.get('content-length', 0))
    if resume:
        file_size = get_file_size(file_path)
        if file_size < total:
            if file_size:
                headers['Range'] = f'bytes={file_size}-'
            time.sleep(random.random())
            save_response_data(get_data(), total, file_path, file_size)
        else:
            print(file_path, ' ✅')
    else:
        save_response_data(response, total, file_path)
