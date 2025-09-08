# -*- coding: UTF-8 -*-
# @Time : 2023/11/15 16:35 
# @Author : 刘洪波
"""
计算相似度的工具
"""
import numpy as np


def cosine_similarity(vector1: np.array, vector2: np.array):
    return vector1.dot(vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


def edit_distance(str_1: str, str_2: str, is_percent: bool = False):
    """编辑距离"""
    l1, l2 = len(str_1) + 1, len(str_2) + 1
    matrix = np.zeros(shape=(l1, l2), dtype=np.int8)
    for i in range(l1):
        matrix[i][0] = i
    for j in range(l2):
        matrix[0][j] = j
    for i in range(1, l1):
        for j in range(1, l2):
            delta = 0 if str_1[i - 1] == str_2[j - 1] else 1
            matrix[i][j] = min(matrix[i - 1][j - 1] + delta,
                               matrix[i - 1][j] + 1,
                               matrix[i][j - 1] + 1)
    if is_percent:
        return 1 - (matrix[-1][-1] / (max(l1, l2) - 1))
    return matrix[-1][-1]


