# -*- coding: UTF-8 -*-
# @Time : 2023/11/15 18:18 
# @Author : 刘洪波
import jieba
from bigtools.stopwords import stopwords


def get_keywords_from_text(text: str):
    """从文本中获取关键词"""
    return [i.strip() for i in jieba.cut(text) if i.strip() and i.strip() not in stopwords]
