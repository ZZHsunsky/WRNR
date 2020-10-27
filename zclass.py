'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-16 15:39:03
LastEditors: zehao zhao
LastEditTime: 2020-10-16 16:05:55
'''
from typing import List, Dict
import random
import numpy as np
from collections import defaultdict, Counter
import math


class TreeNode:

    def __init__(self, v, w):
        self.v = v # 节点编号
        self.w = w # 节点权值
        self.get_sub = False
        self.fathers: Dict[int, TreeNode] = {}
        self.children: Dict[int, TreeNode] = {}
    
    def add_child(self, node):
        self.children[node.v] = node

    def get_child_length(self) -> int:
        return len(list(self.children.keys()))
    
    def set_father(self, f):
        if f not in self.fathers:
            self.fathers[f.v] = f

class Bitmap:
    def __init__(self, length):
        self.bitmap = 0

    def set(self, num):
        self.bitmap |= (1 << num)
    
    def or_other_bitmap(self, other):
        self.bitmap |= other.bitmap

    def or_other_bitmap_ret_diff(self, other) -> List[int]:
        xor = self.bitmap ^ other.bitmap
        self.bitmap |= other.bitmap
        return other.bitmap & xor


def convert_bitmap_to_num_arr(bitmap: Bitmap) -> List[int]:
    """
        将bitmap中的为1的下标按照数组的方式返回
    """
    return convert_int_to_num_arr(bitmap.bitmap)



def convert_int_to_num_arr(bitmap: List[int]) -> List[int]:
    if bitmap == 0:
        return []
    
    ret = []
    for bit_idx in range(int(math.log2(bitmap)) + 1):
        if bitmap & (1 << bit_idx):
            ret.append(bit_idx)
    return ret
    
class ZGraph:
    """
        graph data structure to store the network
    """

    def __init__(self, sub_model=False):
        self.network = dict()
        self.sub_model = sub_model
        self.max_v = 0
        self.cnt_e = 0
        self.candidate_bitmaps = None

    def add_vertex(self, vertex: int):
        if vertex not in self.network:
            self.network[vertex] = dict()
            self.max_v = max(self.max_v, vertex)
    
    def add_edge(self, s: int, e: int, w: float):
        """
        :param s: start vertex
        :param e: end vertex
        :param w: edge weight or proability
        """
        if s == e:
            return
        self.add_vertex(s)
        self.add_vertex(e)
        if e in self.network[s]:
            return
        
        self.cnt_e += 1
        if not self.sub_model:
            self.network[s][e] = w
        elif random.random() < w:
            self.network[s][e] = w
    
    def get_network_candidates(self) -> List[int]:
        """
            获得网络中种子节点的候选者（出度大于等于1）
        """
        candidates = []
        for vertex in self.network:
            if len(self.network[vertex].items()) > 0:
                candidates.append(vertex)
        return candidates
    
    def get_candidate_bitmap(self, vertex: int) ->Bitmap:
        """
            获得网络中种子节点的候选者以及用bitmap表示其影响范围
        """
        if self.candidate_bitmaps == None:
            self.build_cnadiates_bitmaps()
        
        if vertex in self.candidate_bitmaps:
            return self.candidate_bitmaps[vertex]
        else:
            return None
        
    def build_cnadiates_bitmaps(self):
        candidate_bitmaps = {}
        for vertex in self.network:
            if len(self.network[vertex].items()) > 0:
                bitmap = Bitmap(self.max_v)
                bitmap.set(vertex)
                for k in self.network[vertex].keys():
                    bitmap.set(k)
                candidate_bitmaps[vertex] = bitmap
        
        self.candidate_bitmaps = candidate_bitmaps
    
    def get_out_degree(self, vertex: int) -> int:
        """
            获取指定节点的出度
        """
        return len(self.network[vertex])
    
    def get_neighbors(self, vertex: int) -> List[tuple]:
        """
            获取指定节点的邻居以及对应边上的w
        """
        if vertex in self.network:
            return self.network[vertex].items()
        else:
            return []
    
    def get_neighbors_keys(self, vertex: int) -> List[int]:
        """
            获取指定节点的邻居编号
        """
        if vertex in self.network:
            return list(self.network[vertex].keys())
        else:
            return []
    
    def get_neighbors_keys_with_w(self, vertex: int) -> List[int]:
        """
            以边上的概率w返回指定节点的邻居编号
        """
        if vertex in self.network:
            ret = [x for x in self.network[vertex].keys() if np.random.rand() <= self.network[vertex][x]]
            return ret
        else:
            return []

    def remove_edge(self, s:int, e:int):
        """
            删除指定边，如果其存在的话
        """
        if s in self.network:
            if e in self.network[s]:
                del self.network[s][e]
    
    def save_to_txt(self, idx: int, network_type: str):
        """
            将当前网络数据保存在txt中
            主要是为了保存子图
        """
        file_dir = "./Data/Sub-" + network_type
        file_path = file_dir + "/" + str(idx) + '.txt'
        file = open(file_path, 'w')

        for vertex, adj in self.network.items():
            for neighbor, w in adj.items():
                line = str(vertex) + " " + str(neighbor) + " " + str(w) + "\r"
                file.write(line)
        file.close()
    
    def get_a_rr_set(self) -> set:
        """
            生成Reverse Reachab Set
        """
        vertex = random.choice(list(self.network.keys()))
        q = [vertex]
        rr = set(q)
        while q:
            vertex = q.pop(0)
            neighbors = self.get_neighbors_keys_with_w(vertex)
            q = [u for u in neighbors if u not in rr]
            rr.update(neighbors)
        return rr
    
    def get_random_edges(self) -> Dict:
        edges = {}
        for vertex in self.network:
            neighbors = self.get_neighbors_keys_with_w(vertex)
            if len(neighbors) > 0:
                edges[vertex] = neighbors
        return edges
    
    def draw_with_networkx(self):
        if len(self.network.keys()) > 100:
            return
        import pygraphviz as pgv

        g = pgv.AGraph(directed=True)

        for v in self.network.keys():
            if v not in g.nodes():
                g.add_node(v)
            for u in self.get_neighbors_keys(v):
                if u not in g.nodes():
                    g.add_node(u)
                g.add_edge(v, u, label=str(self.network[v][u]))
        
        
        g.layout(prog='dot') # use dot
        g.draw('b.png', prog="dot")
    
    def draw_ont_node(self, v):
        if len(self.network.keys()) > 100 or v not in self.network:
            return
        import pygraphviz as pgv

        g = pgv.AGraph(directed=True)
        
        q = [v]
        while q:
            cur = q.pop()
            for v in self.get_neighbors_keys(cur):
                w = self.network[cur][v]
                q.append(v)
                g.add_edge(cur, v, label=str(round(w, 3)))
        g.layout(prog='dot') # use dot
        g.draw('b.png', prog="dot")
        
        
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

