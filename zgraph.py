'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-16 15:39:03
LastEditors: zehao zhao
LastEditTime: 2020-10-09 18:02:51
'''
from typing import List, Dict
import random
from zbitmap import Bitmap
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
            ret = [x for x in self.network[vertex].keys() if random.random() < self.network[vertex][x]]
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

    def find_scc(self):
        n = self.max_v + 1
        dfn = [-1 for i in range(n)]
        low = [-1 for i in range(n)]
        in_statck = [False for i in range(n)]
        dfncnt = 0
        scc = [] # 用来保存 strong connect commponet 编号
        sc = 0
        stack = [-1 for i in range(n)]
        tp = 0 # 表示栈顶
        def tarjan(u):
            nonlocal dfn, low, dfncnt, scc, sc, tp

            low[u] = dfn[u] =dfncnt
            dfncnt += 1

            tp += 1
            stack[tp] = u

            in_statck[u] = True
            neighbors = self.get_neighbors_keys(u)

            for v in neighbors:
                if dfn[v] == -1:
                    tarjan(v)
                    low[u] = min(low[u], low[v])
                elif in_statck[v]:
                    low[u] = min(low[u], dfn[v])
            
            if dfn[u] == low[u]:
                sc += 1
                temp_scc = []
                while stack[tp] != u:
                    temp_scc.append(stack[tp])
                    in_statck[stack[tp]] = False
                    tp -= 1
                
                temp_scc.append(stack[tp])
                in_statck[stack[tp]] = False
                tp -= 1
                scc.append(temp_scc)
        
        for u in self.get_network_candidates():
            if dfn[u] == -1:
                tarjan(u)
        
        print("共有强连通量：", sc)
        print("共有节点：", self.max_v)

if __name__ == "__main__":
    g = ZGraph()
    edges = [[0, 2], [2, 1], [1, 0], [2, 3], [3, 4], [4, 5], [3, 6], [6, 2], [2, 7], [7, 6]]
    for edge in edges:
        s, e = edge
        w = 1
        g.add_edge(s, e, w)
    g.find_scc()