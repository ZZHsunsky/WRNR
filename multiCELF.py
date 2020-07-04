import numpy as np
import pandas as pd
import time
import imbase
import multiprocessing  as mp
import sys


def multiMargain(G, p, mc, name, param, result_dict, result_lock):
    Q = []
    for idx in param:
        spread = []
        for _ in range(mc):
            new_active, A = [idx], [idx]
            while new_active:
                temp = G.loc[G['source'].isin(new_active)]

                targets = temp['target'].tolist()

                success  = np.random.uniform(0,1,len(targets)) < 0.1
                new_ones = np.extract(success, targets)

                new_active = list(set(new_ones) - set(A))
                A += new_active 
            spread.append(len(A))
        Q.append([idx, np.mean(spread)])
    with result_lock:
        result_dict[name] = Q
    return


def main(G, k=50, dataset="Random", p=0.1, mc=1000):

    candidates = np.unique(G['source']).tolist()

    # 读取CPU核心数量，加入进程池
    num_cores = int(mp.cpu_count())
    pool = mp.Pool(num_cores)

    # Source节点个数
    n = len(candidates)
    
    step = n // num_cores

    # 对参数进行分片
    param_dict = {}
    for _ in range(num_cores):
        if _ == num_cores - 1:
            param_dict['task' + str(_ + 1)] = candidates[_ * step:]
        else:
            param_dict['task' + str(_ + 1)] = candidates[_ * step: (_ + 1) * step]
    
    # 共享变量
    manager = mp.Manager()
    managed_locker = manager.Lock()
    managed_dict = manager.dict()

    # 开始执行多进程函数
    start_time = time.time()
    results = [pool.apply_async(multiMargain, args=(G, p, mc, name, param, managed_dict, managed_locker)) for name, param in param_dict.items()]
    results = [p.get() for p in results]
    # 拼接最后结果
    Q = []
    for key in managed_dict:
        Q += managed_dict[key]
    SEED , timelapse, spread = [], [], 0

    Q = sorted(Q, key = lambda x: x[1],reverse=True)
    index_ = dataset + '-CELF-'
    index = []
    for _ in range(k):

        index.append(index_ + str(_ + 1))
        check = False    

        while not check:     
            current = Q[0][0]      
            Q[0] = (current, imbase.IC(G, SEED + [ current ], p=0.1, mc=3000) - spread)
            Q = sorted(Q, key = lambda x: x[1], reverse=True)
            check = Q[0][0] == current

        SEED.append(Q[0][0])
        spread = Q[0][1]
        Q = Q[1:]
        timelapse.append(round(time.time() - start_time, 4))
    
    with open('Experiment.txt', 'a+') as f:
        for _ in range(k):
            f.write("%s    %d    %f\n" %(index[_], SEED[_], timelapse[_]))

    return (sorted(SEED), timelapse)
