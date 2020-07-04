import numpy as np
import pandas as pd
import time
import imbase
import random
import multiprocessing  as mp
from collections import Counter
import sys


def multiMargain(G, p, name, param, result_dict, result_lock):
    Q = []
    for idx in range(param):
        source = random.choice(np.unique(G['source']))
        g = G.copy().loc[np.random.uniform(0, 1, G.shape[0]) < p]
        new_nodes, RRS0 = [source], [source]

        while new_nodes:

            temp = g.loc[g['target'].isin(new_nodes)]
            temp = temp['source'].tolist()

            RRS = list(set(RRS0 + temp))

            new_nodes = list(set(RRS) - set(RRS0))

            RRS0 = RRS[:]
        Q.append(RRS)
    
    with result_lock:
        result_dict[name] = Q
    return

def main(G, k=50, dataset="Random", p=0.1, mc=50000):

    # 读取CPU核心数量，加入进程池
    num_cores = int(mp.cpu_count())
    pool = mp.Pool(num_cores)

    step = mc // num_cores

    # 对参数进行分片
    param_dict = {}
    for _ in range(num_cores):
        if _ == num_cores - 1:
            param_dict['task' + str(_ + 1)] = mc - _ * step
        else:
            param_dict['task' + str(_ + 1)] = step
    
    # 共享变量
    manager = mp.Manager()
    managed_locker = manager.Lock()
    managed_dict = manager.dict()

    # 开始执行多进程函数
    start_time = time.time()
    results = [pool.apply_async(multiMargain, args=(G, p, name, param, managed_dict, managed_locker)) for name, param in param_dict.items()]
    results = [p.get() for p in results]
    
    # 拼接最后结果
    R = []
    for key in managed_dict:
        R += managed_dict[key]

    SEED , timelapse = [], []

    index_ = dataset + '-RIS-'
    index = []
    for _ in range(k):

        index.append(index_ + str(_ + 1))
        flat_list = [item for sublist in R for item in sublist]
        seed = Counter(flat_list).most_common()[0][0]
        SEED.append(seed)

        # Remove RRSs containing last chosen seed
        R = [rrs for rrs in R if seed not in rrs]
        timelapse.append(round(time.time() - start_time, 4))

    with open('Experiment.txt', 'a+') as f:
        for _ in range(k):
            f.write("%s    %d    %f\n" %(index[_], SEED[_], timelapse[_]))
    return(sorted(SEED), timelapse)