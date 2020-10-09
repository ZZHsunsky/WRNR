'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-17 10:41:50
LastEditors: zehao zhao
LastEditTime: 2020-09-17 18:16:02
'''
from typing import List
import math


class Bitmap:
    def __init__(self, length):
        self.bitmap = 0

    def set(self, num):
        self.bitmap |= (1 << num)
    
    def or_other_bitmap(self, other):
        self.bitmap |= other.bitmap

    def or_other_bitmap_ret_diff(self, other) -> List[int]:
        xor = self.bitmap ^ other.bitmap
        self.bitmap |= other.bitmap
        return other.bitmap & xor


def convert_bitmap_to_num_arr(bitmap: Bitmap) -> List[int]:
    """
        将bitmap中的为1的下标按照数组的方式返回
    """
    return convert_int_to_num_arr(bitmap.bitmap)



def convert_int_to_num_arr(bitmap: List[int]) -> List[int]:
    if bitmap == 0:
        return []
    
    ret = []
    for bit_idx in range(int(math.log2(bitmap)) + 1):
        if bitmap & (1 << bit_idx):
            ret.append(bit_idx)
    return ret
    
