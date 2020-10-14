'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-12 11:08:11
LastEditors: zehao zhao
LastEditTime: 2020-10-14 18:47:40
'''
from zutils import *
from zclass import ZBitGraph, TreeNode
import logging
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed, Future
from multiprocessing import cpu_count

class ZMDTree:
    def __init__(self, v, sc):
        self.v = v                              # 节点编号
        self.sc = sc                            # 强连通分量编号
        self.in_children = defaultdict(int)     # 记录同一强连通分量的可到达节点
        self.out_children = defaultdict(int)    # 记录指向别的连通分量的可到达节点，key保存分量编号，val保存节点编号
        self.has_visited_out = False            # 记录当前节点是否已经遍历完了out children
        self.father = defaultdict(int)          # 记录自己的父亲
        self.sigma = 1                          # 选择该节点的影响范围的期望
        self.in_sigma = -1                      # 内部连通量的影响范围
        self.out_sigma = -1                     # 外部影响范围

    def add_in_child(self, v, w):
        if v not in self.out_children:
            self.in_children[v] = (1 - w)
        else:
            self.in_children[v] *= (1 - w)
    
    def add_out_children(self, sc, w):
        if sc not in self.out_children:
            self.out_children[sc] = (1 - w)
        else:
            self.out_children[sc] *= (1 - w)               # 指向同一个分量可能有好几条边
    
    def add_father(self, v, w):
        self.father[v] = w                      # 在计算完之后添加父亲，这时边的权重已经确定
    
    def get_in_children_sigma(self):
        if self.in_sigma == -1:
            temp = 0
            for i in list(self.in_children.values()):
                temp += (1 - i)
            self.in_sigma = 1 + temp
        return self.in_sigma
    
    def get_out_children_sigma(self):
        if self.out_sigma == -1:
            temp = 0
            for i in list(self.out_children.values()):
                temp += (1 - i)
            self.out_sigma = temp
        return self.out_sigma
    
    def get_sigma(self, forest: dict):
        sigma = self.get_in_children_sigma() + self.get_out_children_sigma()
        for v, w in self.in_children.items():
            sigma += w * forest[v].get_out_children_sigma()
        return sigma

@fn_timer
def zmd_node_select(k: int, g: ZGraph):
    n = g.max_v + 1
    dfn = [-1 for i in range(n)]
    low = [-1 for i in range(n)]
    in_statck = [False for i in range(n)]
    dfncnt = 0

    sc = 0                                      # 强连通量的个数
    scc = [-1 for i in range(n)]                # 用来保存强连通分量的编号

    forest: Dict[int, ZMDTree] = {}             # 用来保存缩点后的森林

    stack = [-1 for i in range(n)]
    tp = 0 # 表示栈顶
    def tarjan(u):
        nonlocal dfn, low, dfncnt, scc, sc, tp

        low[u] = dfn[u] = dfncnt
        dfncnt += 1

        tp += 1
        stack[tp] = u

        in_statck[u] = True
        neighbors = g.get_neighbors_keys(u)

        for v in neighbors:
            if dfn[v] == -1:
                tarjan(v)
                low[u] = min(low[u], low[v])
            elif in_statck[v]:
                low[u] = min(low[u], dfn[v])
        
        if dfn[u] == low[u]:
            while stack[tp] != u:
                scc[stack[tp]] = sc
                in_statck[stack[tp]] = False
                tp -= 1
            
            scc[u] = sc
            in_statck[u] = False
            tp -= 1
            sc += 1

    network_candidates = g.get_network_candidates()
    
    for u in network_candidates:
        if dfn[u] == -1:
            tarjan(u)

    cnt = 0
    for i in range(len(scc)):
        if scc[i] == 1627:
            cnt += 1
    for u in g.network.keys():
        forest[u] = ZMDTree(u, scc[u])
    
    logging.info("构建了{}个强连通分量".format(sc))

    tempg = ZGraph()
    visited=dict()
    def in_dfs(root: int, ancestor: ZMDTree, last = -1, decay = 1):
        nonlocal visited
        if decay < 10 ** (-7):
            return

        if last > -1 and root == ancestor.v:
            return

        if last > -1:
            decay = decay * g.network[last][root]
            ancestor.add_in_child(root, decay)

        visited[root] = True
        for v in g.get_neighbors_keys(root):
            if scc[v] != ancestor.sc:
                continue
            if v == last:
                continue
            if visited.get(v, False):
                continue
            
            in_dfs(v, ancestor, root, decay)


    # 构造强连通分量内部的连接
    for u in network_candidates:
        ancestor = forest[u]
        visited.clear()
        in_dfs(u, ancestor)
    logging.info("完成了连通分量内部的构造")

    
    def out_dfs(root: int, ancestor: ZMDTree, last = -1, decay=1):

        if decay < 10 ** (-7):
            return

        if last > -1:
            decay = decay * g.network[last][root]
            in_sigma = forest[root].get_in_children_sigma()
            ancestor.add_out_children(root, decay * in_sigma)
        
        if forest[root].has_visited_out:
            for v, w in forest[root].out_children.items():
                ancestor.add_out_children(v, decay * (1 - w))
            return

        # visited[root] = True
        for v in g.get_neighbors_keys(root):

            if scc[v] == ancestor.sc:
                continue

            if scc[root] == scc[v]:
                continue

            out_dfs(v, ancestor, root, decay)

        forest[root].has_visited_out = True
            

    # 构造强连通分量之间的连接  
    for u in network_candidates:
        ancestor = forest[u]
        if ancestor.has_visited_out:
            continue
        out_dfs(u, ancestor)
    
    logging.info("完成了连通分量外部的构造")
    
    Q = []
    for u in network_candidates:
        ancestor = forest[u]
        sigma = ancestor.get_sigma(forest)
        Q.append([sigma, u])
    
    Q = sorted(Q, key=lambda x: x[0], reverse=True)

    best = Q[0][1]
    # print(forest[best].in_children)
    # print(forest[best].out_children)
    print(forest[best].get_sigma(forest))
    
    draw_one_node_with_in_children(forest[best])
    # draw_one_node_with_out_children(forest[best])

    Seed = []
    for i in range(k):
        Seed.append(Q[i][1])

    return Seed

def draw_one_node_with_out_children(node: ZMDTree):
    import pygraphviz as pgv

    g = pgv.AGraph(directed=True)

    for v, w in node.out_children.items():
        g.add_edge(node.v, v, label=str(round(1-w, 3)))
    
    g.layout(prog='dot') # use dot
    g.draw('c.png', prog="dot")

def draw_one_node_with_in_children(node: ZMDTree):
    import pygraphviz as pgv

    g = pgv.AGraph(directed=True)

    for v, w in node.in_children.items():
        g.add_edge(node.v, v, label=str(round(1-w, 3)))
    
    g.layout(prog='dot') # use dot
    g.draw('c.png', prog="dot")