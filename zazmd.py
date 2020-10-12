'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-12 11:08:11
LastEditors: zehao zhao
LastEditTime: 2020-10-12 18:53:34
'''
from zutils import *
from zclass import ZBitGraph, TreeNode
import logging
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed, Future
from multiprocessing import cpu_count

class ZMDTree:
    def __init__(self, v, sc):
        self.v = v                        # 节点编号
        self.sc = sc                      # 强连通分量编号
        self.child = defaultdict(int)     # 记录自己的孩子
        self.father = defaultdict(int)    # 记录自己的父亲、
        self.sigma = 1                    # 选择该节点的影响范围的期望

    def add_child(self, v, w):
        self.child[v] += w                # 可能存在指向孩子的多重边
    
    def add_father(self, v, w):
        self.father[v] = w                # 在计算完之后添加父亲，这时边的权重已经确定

def build_two_deep_tree(g: ZGraph):
    

     