import numpy as np
import pandas as pd
import time
import imbase
import random
import multiprocessing  as mp
import sys


def multiIC(G, p, name, param, result_dict, result_lock):
    spread = []
    mc, S = param[0], param[1]
    for _ in range(mc):
        
        # Simulate propagation process      
        new_active, A = S[:], S[:]
        while new_active:
            
            temp = G.loc[G['source'].isin(new_active)]

            targets = temp['target'].tolist()

            success  = np.random.uniform(0,1,len(targets)) < p
            new_ones = np.extract(success, targets)

            new_active = list(set(new_ones) - set(A))
                        
            A += new_active
            
        spread.append(len(A))
    with result_lock:
        result_dict[name] = np.mean(spread)
    return

def main(G, dataset, S, p=0.1, mc = 10000, num_cores = 8):

    # 读取CPU核心数量，加入进程池
    pool = mp.Pool(num_cores)

    step = mc // num_cores

    # 对参数进行分片
    param_dict = {}
    for _ in range(num_cores):
        if _ == num_cores - 1:
            param_dict['task' + str(_ + 1)] = [mc - _ * step, S]
        else:
            param_dict['task' + str(_ + 1)] = [step, S]
    
    # 共享变量
    manager = mp.Manager()
    managed_locker = manager.Lock()
    managed_dict = manager.dict()

    # 开始执行多进程函数
    start_time = time.time()
    results = [pool.apply_async(multiIC, args=(G, p, name, param, managed_dict, managed_locker)) for name, param in param_dict.items()]
    results = [p.get() for p in results]
    
    # 拼接最后结果
    R = 0
    for key in managed_dict:
        R += managed_dict[key]
    
    return round(R / num_cores, 4), round(time.time() - start_time, 2)

if __name__ == "__main__":
    main()

   