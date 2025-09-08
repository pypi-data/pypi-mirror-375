# -*- coding: UTF-8 -*-
# @Time : 2023/10/19 14:20 
# @Author : 刘洪波
import hashlib


def get_new_hash_object_dict():
    return {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha224': hashlib.sha224(),
        'sha256': hashlib.sha256(),
        'sha384': hashlib.sha384(),
        'sha512': hashlib.sha512(),
        'sha3_224': hashlib.sha3_224(),
        'sha3_256': hashlib.sha3_256(),
        'sha3_384': hashlib.sha3_384(),
        'sha3_512': hashlib.sha3_512(),
        'shake_128': hashlib.shake_128(),  # 生成指定字符长度的哈希, 通过 hexdigest(100) 控制长度
        'shake_256': hashlib.shake_256(),  # 生成指定字符长度的哈希, 通过 hexdigest(100) 控制长度
        'blake2b': hashlib.blake2b(),  # 生成最高512位的任意长度哈希, 长度随机
        'blake2s': hashlib.blake2s(),  # 生成最高256位的任意长度哈希, 长度随机
    }


def generate_hash_value(input_str: str, hash_function: str = 'md5', length: int = None) -> str:
    """
    生成 hash 值
    :param input_str: 输入字符串
    :param hash_function: hash方法
    :param length: 生成的hash 长度，仅对 shake_128 和 shake_256 有效
    :return: 只能返回十六进制结果，不返回二进制结果
    """
    input_str = input_str.encode()
    hash_object_dict = get_new_hash_object_dict()
    hash_object = hash_object_dict.get(hash_function)
    if hash_object:
        hash_object.update(input_str)
        if length:
            if hash_function in {'shake_128', 'shake_256'}:
                return hash_object.hexdigest(length)
            else:
                raise ValueError(f'length is not None, hash_function not in ["shake_128", "shake_256"], '
                                 f'please check hash_function or length')
        else:
            return hash_object.hexdigest()
    else:
        raise ValueError(f'hash_function not in hash_object_dict, please check hash_function')


"""
note:
- 使用 hash_object.hexdigest() 得到十六进制结果
- 使用 hash_object.digest() 得到二进制结果
- hexdigest与digest的转换
    - 需要使用binascii模块的hexlify()和unhexlify()这两个方法。
    - hexlify()将二进制结果转换成十六进制结果，unhexlify()反之。
        import binascii
        binascii.hexlify()
        binascii.unhexlify()
"""
