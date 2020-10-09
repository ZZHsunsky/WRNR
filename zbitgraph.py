'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-25 09:23:52
LastEditors: zehao zhao
LastEditTime: 2020-09-25 11:05:26
'''
from collections import defaultdict
from typing import List

def pick_different(s: int, t: int) -> List[int]:
    return pick_one_set_bits(t & ( ~ ( 1 << s )))

def pick_one_set_bits(t: int) -> List[int]:
    ret = []
    idx = 0
    while t:
        if t & 1:
            ret.append(idx)
        idx += 1
        t >>= 1
    return ret

def cnt_onet_set_bits(t: int) -> int:
    cnt = 0
    while t:
        if t & 1:
            cnt += 1
        t >>= 1
    return cnt

class ZBitGraph:
    """
        构造网络拓扑图，通过BitMap保存
    """
    def __init__(self):
        self.network = dict()
        self.max_v = 0
        self.cnt_e = 0
    
    def add_vertex(self, vertex: int):
        if vertex not in self.network:
            self.network[vertex] = 1 << vertex
            self.max_v = max(self.max_v, vertex)
    
    def add_edge(self, s: int, e: int):
        self.add_vertex(s)
        self.add_vertex(e)

        if self.network[s] & (1 << e) == 1:
            return
        else:
            self.network[s] |= (1 << e)
            self.cnt_e += 1
    
    def simulate_propagation(self):
        visited = defaultdict(bool)

        for vertex in self.network.keys():
            all_actived = self.network[vertex]
            new_actived = pick_different(vertex, all_actived)
            while new_actived:
                temp_actived = all_actived
                for e in new_actived:
                    temp_actived |= self.network[e]
                    if visited[e]:
                        all_actived |= self.network[e]
                new_actived = pick_one_set_bits(temp_actived ^ all_actived)
                all_actived |= temp_actived

            visited[vertex] = True
            self.network[vertex] = all_actived
    
    def get_vertex_spread(self, vertex: int) -> int:
        if vertex not in self.network:
            return 0
        return cnt_onet_set_bits(self.network[vertex])

    def discount_spread(self, spread:int):
        for vertex in self.network.keys():
            xor = self.network[vertex] ^ spread
            self.network[vertex] &= xor
    
if __name__ == "__main__":
    g = ZBitGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 2)
    g.add_edge(1, 4)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    g.add_edge(3, 5)
    g.add_edge(5, 6)
    g.add_edge(6, 2)
    g.simulate_propagation()
    for k, v in g.network.items():
        print(k, bin(v))
