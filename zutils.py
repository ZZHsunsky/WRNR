
'''
Descripttion: 
version: 
Author: sueRimn
Date: 2020-09-14 18:24:34
LastEditors: zehao zhao
LastEditTime: 2020-09-25 10:29:40
'''

import time
import math
from typing import List
from zgraph import *
from zbitmap import *
from collections import Counter
from functools import wraps
from tqdm import *


def blue_print(s: str):
    return ("\033[1;34m{}\033[0m".format(s))

def orange_print(s: str):
    return ("\033[0;33m{}\033[0m".format(s))

def green_print(s: str):
    return ("\033[0;32m{}\033[0m".format(s))

def red_print(s: str):
    return ("\033[0;31m{}\033[0m".format(s))

def cyan_print(s: str):
    return ("\033[0;36m{}\033[0m".format(s))

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        print(  "\n" + "*" * 30 + "\n" + blue_print("[Start] ") + green_print(getattr(function, '__name__').upper()) +"\n" + "*" * 30)
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print(blue_print("[Done] ") + green_print(getattr(function, '__name__').upper()) + orange_print(" " + str(t1-t0)) + " Seconds")
        return result
    return function_timer

def build_sub_networks(network_type: str, cnt: int):
    """
        生成网络子图
    :param network_type: 数据集名称
    :param cnt: 子集的数量
    """
    import os
    file_dir = "./Data/Sub-" + network_type
    files = os.listdir(file_dir)

    for file in files:
        if os.path.isdir(file):
            continue
        os.remove(file_dir + "/" + file)

    print(blue_print("[Start] ") + green_print(network_type + " Dataset ") + "Build Sub Networks!")
    for i in tqdm(range(cnt)):
        g = ZGraph(sub_model=True)
        load_network(g, network_type)
        g.save_to_txt(i, network_type)



def fix_w_in_network(network_type):
    file_dir = "./Data/"
    file_path = file_dir + network_type + '.txt'
    import os
    if not os.path.exists(file_path):
        print(red_print("[Error] ") + green_print(network_type + " Dataset ") + "not exists!")
        return None
    
    lines = open(file_path).readlines()
    fix_file_path = file_dir + network_type + 'Fix.txt'
    fix_file = open(fix_file_path, 'w')
    fix_file.write(lines[0])
    print(blue_print("[Start] ") + green_print(network_type + " Dataset ") + "Fix Action!")
    for line in tqdm(lines[1:]):
        w = round(random.uniform(0, 0.3), 3)
        w = " " + str(w) + "\n"
        fix_file.write(line.strip() + w)
    fix_file.close()

def load_network(g: ZGraph, network_type: str, reverse=False):
    """
    :param network_type: 数据集类型，可选值为 Random，NetHept
    """
    if network_type == "Random":
        return
    
    # 数据集文件夹的路径
    file_dir = "./Data/"
    # 数据集的真实路径
    file_path = file_dir + network_type + ".txt"
    load_network_from_data(g, file_path, reverse)


def load_network_from_data(g: ZGraph, file_path: str, reverse=False):
    """
        从文件中加载网络关系到ZGraph实例中
    :param g: ZGraph实例
    :param file_path: 文件路径
    """
    data_lines = open(file_path, 'r').readlines()

    for data_line in data_lines[1:]:
        s, e, w = data_line.split()
        if reverse:
            g.add_edge(int(e), int(s), float(w))
        else:
            g.add_edge(int(s), int(e), float(w))

def load_sub_networks(network_type: str) -> List[ZGraph]:
    """
        加载指定网络类型的子网络，遍历指定路径下的文件，返回ZGraph数组
    :param network_type: 数据集名称
    :return networks: 子网络图生成的 ZGraph数组
    """
    import os
    file_dir = "./Data/Sub-" + network_type
    files = os.listdir(file_dir)
    networks = []
    for file in files:
        if os.path.isdir(file):
            continue
        g = ZGraph(sub_model=False)
        load_network_from_data(g, file_dir + "/" + file)
        networks.append(g)
    return networks

def calc_celf_sigma_in_network(s: List[int], g: ZGraph, mc=100) -> float:
    mc_sigma = [len(calc_sigma_in_network(s, g, with_w=True)) for i in range(mc)]
    return sum(mc_sigma) / mc

def calc_sigma_in_network(s: List[int], g: ZGraph, with_w=False) -> set:
    """
        计算种子节点集合在一个网络中的影响范围
    :param s: 种子节点集合
    :paam g: ZGraph网络实例
    :return all_actived_set: 可以影响的节点集合（包括种子集合本身）
    """
    actived_set = set(s)
    all_actived_set = actived_set.copy()

    while actived_set:
        temp = set()
        for vertex in actived_set:
            if with_w:
                neighbors = g.get_neighbors_keys_with_w(vertex)
            else:
                neighbors = g.get_neighbors_keys(vertex)
            for neighbor in neighbors:
                if neighbor not in all_actived_set:
                    temp.add(neighbor)
        all_actived_set.update(temp)
        actived_set = temp
    
    return all_actived_set


def calc_sigma_in_sub_networks(s: List[int], networks: List[ZGraph]) -> float:
    """
        计算种子节点集合在子网络集合中的影响范围
    :param s: 种子节点集合
    :param networks: ZGraph网络实例数组
    :return sigma: 影响节点数的平均值
    """
    sigma = 0
    for g in networks:
        temp_actived_set = calc_sigma_in_network(s, g)
        sigma += len(temp_actived_set)
    
    sigma = round(sigma / len(networks), 3)
    print("Sigma is " + cyan_print(str(sigma)) + " with Seed " + cyan_print(str(s)))
    return sigma


def calc_sigma_in_random_networks(s: List[int], g: ZGraph, mc=1000) -> float:
    sigma = 0
    for i in range(mc):
        temp_actived_set = calc_sigma_in_network(s, g, with_w=True)
        sigma += len(temp_actived_set)
    
    sigma = round(sigma / mc, 3)
    print("Sigma is " + cyan_print(str(sigma)) + " with Seed " + cyan_print(str(s)))
    return sigma

def calc_sigma_in_network_with_bitmap(s: List[int], g: ZGraph, with_w=False) -> List[int]:
    actived_set = set(s)
    sigma = Bitmap(g.max_v)

    while actived_set:
        temp_bitmap = Bitmap(g.max_v)
        for v in actived_set:
            other_bitmap = g.get_candidate_bitmap(v)
            if other_bitmap != None:
                temp_bitmap.or_other_bitmap(other_bitmap)
            else:
                sigma.set(v)
        diff = sigma.or_other_bitmap_ret_diff(temp_bitmap)
        actived_set = convert_int_to_num_arr(diff)
        
    
    return convert_bitmap_to_num_arr(sigma)

def calc_sigma_in_sub_networks_with_bitmap(s: List[int], networks: List[ZGraph]) -> float:
    sigma = sum([len(calc_sigma_in_network_with_bitmap(s, g) for f in networks)])
    return round(sigma / len(networks), 3)


if __name__ == "__main__":
    fix_w_in_network('NetPHY')