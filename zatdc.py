'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-25 10:18:27
LastEditors: zehao zhao
LastEditTime: 2020-10-09 15:52:47
'''
from zutils import *
from zclass import ZBitGraph

@fn_timer
def tdc_node_selection(k: int, g: ZGraph, mc=1000):
    candidates = g.get_network_candidates()
    if k >= len(candidates):
        return candidates
    
    Seed = []
    # for g in tqdm(networks):
    for _ in range(mc):
        Seed.extend(bit_graph_selection(k, g,))
    C = Counter(Seed)
    return [x[0] for x in C.most_common(k)]

def bit_graph_selection(k: int, g: ZGraph) -> List[int]:
    bitG = ZBitGraph()

    for s, es in g.get_random_edges().items():
        for e in es:
            bitG.add_edge(s, e)
    
    bitG.simulate_propagation()
    S = []
    spread = 0

    candidates = g.get_network_candidates()

    for i in range(k):
        if spread > 0:
            bitG.discount_spread(spread)
        # else:
        #     for key, v in bitG.network.items():
        #         print(key, bin(v))

        max_v, best = 0, -1
        for vertex in candidates:
            if vertex in S:
                continue

            temp_spread = bitG.get_vertex_spread(vertex)

            if temp_spread > max_v:
                max_v, best = temp_spread, vertex
        
        spread |= bitG.network[best]
        S.append(best)
    
    return S
