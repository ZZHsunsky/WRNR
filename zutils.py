
'''
Descripttion: 
version: 
Author: sueRimn
Date: 2020-09-14 18:24:34
LastEditors: zehao zhao
LastEditTime: 2020-10-15 11:13:31
'''

import time
import math
import random
import numpy as np
from typing import List, Dict, Set
from zclass import ZGraph, ZBitGraph, Bitmap, TreeNode
from zclass import convert_bitmap_to_num_arr, convert_int_to_num_arr
from collections import Counter
from functools import wraps
from scipy.sparse import coo_matrix
from collections import deque, defaultdict
from tqdm import *
import logging
import csv

budgets_config = {
    'NetHEPTFix': [10, 20, 30, 40, 50, 60, 70, 80],
    'NetPHYFix': [20, 40, 60, 80, 100, 120, 140, 160],
    'EpinionsFix': [3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
}

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
        logging.info("\n" + "*" * 30 + "\n" + blue_print("[Start] ") + green_print(
            getattr(function, '__name__').upper()) + "\n" + "*" * 30)
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        logging.info(blue_print("[Done] ") + green_print(getattr(
            function, '__name__').upper()) + orange_print(" " + str(round(t1-t0, 5))) + " Seconds")
        return result, t1-t0
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

    logging.info(blue_print(
        "[Start] ") + green_print(network_type + " Dataset ") + "Build Sub Networks!")
    for i in tqdm(range(cnt)):
        g = ZGraph(sub_model=True)
        load_network(g, network_type)
        g.save_to_txt(i, network_type)


def fix_w_in_network(network_type):
    file_dir = "./Data/"
    file_path = file_dir + network_type + '.txt'
    import os
    if not os.path.exists(file_path):
        logging.info(red_print(
            "[Error] ") + green_print(network_type + " Dataset ") + "not exists!")
        return None

    lines = open(file_path).readlines()
    fix_file_path = file_dir + network_type + 'Fix.txt'
    fix_file = open(fix_file_path, 'w')
    fix_file.write(lines[0])
    logging.info(blue_print(
        "[Start] ") + green_print(network_type + " Dataset ") + "Fix Action!")
    
    indegree = defaultdict(int)
    for line in lines[1:]:
        s, e = line.split()
        indegree[e] += 1
    
    for line in tqdm(lines[1:]):
        s, e = line.split()
        w = 1 / indegree[e]
        w = " " + str(round(w, 3)) + "\n"
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
    return load_network_from_data(g, file_path, reverse)


def load_network_from_data(g: ZGraph, file_path: str, reverse=False):
    """
        从文件中加载网络关系到ZGraph实例中
    :param g: ZGraph实例
    :param file_path: 文件路径
    """
    data_lines = open(file_path, 'r').readlines()

    _row = []
    _col = []
    _data = []

    for data_line in data_lines[1:]:
        s, e, w = data_line.split()
        s, e, w = int(s), int(e), float(w)

        if reverse:
            g.add_edge(e, s, w)
        else:
            ret = g.add_edge(s, e, w)
            if ret:
                _row.append(s)
                _col.append(e)
                _data.append(w)
    
    n = g.max_v + 1
    sp_a = coo_matrix((_data, (_row, _col)), shape=(n, n))
    return sp_a.tocsr()

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
    mc_sigma = [len(calc_sigma_in_network(s, g, with_w=True))
                for i in range(mc)]
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
    logging.info("Sigma is " + cyan_print(str(sigma)) +
                 " with Seed " + cyan_print(str(s)))
    return sigma


def calc_sigma_in_random_networks(s: List[int], g: ZGraph, mc=1000) -> float:
    sigma = 0
    for i in range(mc):
        temp_actived_set = calc_sigma_in_network(s, g, with_w=True)
        sigma += len(temp_actived_set)

    sigma = round(sigma / mc, 3)
    logging.info("Sigma is " + cyan_print(str(sigma)) +
                 " with Seed " + cyan_print(str(s)))
    return sigma


def calc_sigma_in_networks_with_cost(s: List[int], g: ZGraph, mc=1000, func=None, budget=math.inf):
    if func == None:
        return calc_sigma_in_random_networks(s, g, mc)

    sigma = cost = 0
    for i in range(mc):
        actived_set, actived_cost = calc_sigma_with_cost(
            s, g, mc, func, budget)
        sigma += len(actived_set)
        cost += actived_cost

    sigma = round(sigma / mc, 3)
    cost = round(cost / mc, 3)
    logging.info("Sigma is " + cyan_print(str(sigma)) + ", Cost is " +
                 red_print(str(cost)) + " with Seed " + cyan_print(str(s)))
    
    return sigma, cost


def calc_sigma_with_cost(s: List[int], g: ZGraph, mc, func, budget):
    actived_set = deque(s)
    all_actived_set = set(s)
    all_cost = 0

    while actived_set:
        vertex = actived_set.popleft()

        neighbors = g.get_neighbors_keys_with_w(vertex)

        cnt = 0
        for neighbor in neighbors:
            if neighbor in all_actived_set:
                continue
            if all_cost + func(cnt + 1) > budget:
                return all_actived_set, all_cost + func(cnt)

            all_actived_set.add(neighbor)
            actived_set.append(neighbor)
            cnt += 1

        all_cost += func(cnt)

    return all_actived_set, all_cost


def count_sigma_in_random_networks(s: List[int], g: ZGraph, node, mc=10000) -> dict:
    c = Counter()
    for i in range(mc):
        c.update(calc_sigma_in_network(s, g, with_w=True))

    for k in c.keys():
        c[k] /= mc

    print(sum(c.values()))
    for v, w in node.out_children.items():
        c[v] = abs((1 - w) - c[v])
    c[node.v] -= 1
    print(sum(c.values()))
    # import pprint
    # pprint.pprint(c)
    return c


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
    sigma = sum([len(calc_sigma_in_network_with_bitmap(s, g)
                     for g in networks)])
    return round(sigma / len(networks), 3)


def record_experimnet_result(g: ZGraph, S: List[int], network: str, alg: str, runtime: float):
    spread = []

    for i in range(0, len(S), 5):
        s = calc_sigma_in_random_networks(S[:i+1], g)
        spread.append(s)
    
    with open('./Test/{}.csv'.format(network), 'a+', newline="") as file:
        writer = csv.writer(file)
        spread.insert(0, alg)
        writer.writerow(spread)
    
    with open('./Test/runtime.csv', 'a+', newline="") as file:
        writer = csv.writer(file)
        writer.writerow([alg, runtime])

def record_experiment_cost(g: ZGraph, S: List[int], network: str, alg: str, budgets: List[int], func):

    spread = []
    for budget in budgets:
        s, c = calc_sigma_in_networks_with_cost(S, g, mc=1000, func=func, budget=budget)
        spread.append(s)
    
    with open('./Test/Cost-{}.csv'.format(network), 'a', newline="") as file:
        writer = csv.writer(file)
        spread.insert(0, alg)
        writer.writerow(spread)

if __name__ == "__main__":
    fix_w_in_network('NetHEPT')
    fix_w_in_network('NetPHY')
    fix_w_in_network('Epinions')
