'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-25 10:21:51
LastEditors: zehao zhao
LastEditTime: 2020-09-25 10:40:31
'''
from zutils import *

def violence_in_network(k: int, g: ZGraph) -> List[int]:
    """
        在单独网络中，暴力求解最优解
    """
    # 候选者为所有具有出边的节点
    candidates = g.get_network_candidates()
    if k >= len(candidates):
        return candidates
    # 种子节点集合
    maxSpread =  0
    S, ans = [], []
    
    # 回溯法枚举所有的解
    def backtracking(idx=0, out=set()):
        nonlocal ans, maxSpread
        if len(S) == k:
            # 当前解满足约束，判断是否是最优解
            if len(out | set(S)) > maxSpread:
                ans, maxSpread = S[:], len(out | set(S))
            return
        
        for i in range(idx, len(candidates)):
            S.append(candidates[i])
            backtracking(i+1, calc_sigma_in_network(S, g, with_w=True) | out)
            S.pop()


    backtracking()
    return ans

@fn_timer
def violence_in_sub_networks(k:int, g: ZGraph, mc = 1000) -> List[int]:
    """
        在子图集合中暴力求解
        每一个子集中得到一个解，取出现次数最多的前k个做为最优解
    """
    Seed = []
    # for g in tqdm(networks):
    pbar = tqdm(total=100)
    for _ in range(mc):
        if  _ % (mc // 10) == 0:
            pbar.update(10)
        Seed.extend(violence_in_network(k, g,))
    C = Counter(Seed)
    return [x[0] for x in C.most_common(k)]