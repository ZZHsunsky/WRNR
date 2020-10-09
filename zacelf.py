'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-25 10:22:06
LastEditors: zehao zhao
LastEditTime: 2020-09-25 10:50:40
'''
from zutils import *

@fn_timer
def celf_in_origin_network(k: int, g: ZGraph, mc = 100) ->List[int]:
    """
        使用CELF算法求解，类似于Cache命中来加速
    """
    candidates = g.get_network_candidates()
    if k >= len(candidates):
        return candidates

    sigmas = []
    pbar = tqdm(total=100)
    for _, vertex  in enumerate(candidates):
        if  _ % (len(candidates) // 10) == 0:
            pbar.update(10)
        sigmas.append(calc_celf_sigma_in_network([vertex], g, mc=mc))

    Q = sorted(zip(candidates,sigmas), key = lambda x: x[1],reverse=True)

    S, spread, Q = [Q[0][0]], Q[0][1], Q[1:]
    
    for _ in range(k-1):    
        check = False      
        while not check:
            
            current = Q[0][0]
            Q[0] = (current, calc_celf_sigma_in_network(S+[current], g, mc=mc) - spread)
            Q = sorted(Q, key = lambda x: x[1], reverse=True)

            check = Q[0][0] == current

        S.append(Q[0][0])    

        Q = Q[1:]
    return S

@fn_timer
def max_degree_in_origin_network(k: int, g: ZGraph) -> List[int]:
    candidates = g.get_network_candidates()
    if k >= len(candidates):
        return candidates
    
    degree = [g.get_out_degree(vertex) for vertex in candidates]
    Q = sorted(zip(candidates, degree), key= lambda x: x[1], reverse=True)
    S = [Q[i][0] for i in range(k)]
    return S