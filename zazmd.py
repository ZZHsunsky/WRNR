'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-12 11:08:11
LastEditors: zehao zhao
LastEditTime: 2020-10-16 20:13:19
'''
from zutils import *
from zclass import ZBitGraph, TreeNode
import logging
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, as_completed, Future
from multiprocessing import cpu_count

class ZMDTree:
    def __init__(self, v, sc):
        self.v = v                              # 节点编号
        self.sc = sc                            # 强连通分量编号
        self.in_children = defaultdict(int)     # 记录同一强连通分量的可到达节点
        self.out_children = defaultdict(int)    # 记录指向别的连通分量的可到达节点，key保存分量编号，val保存节点编号
        self.has_visited_in = False             # 记录当前节点是否已经遍历完了in childrn
        self.has_visited_out = False            # 记录当前节点是否已经遍历完了out children
        self.father = defaultdict(int)          # 记录自己的父亲
        self.sigma = 1                          # 选择该节点的影响范围的期望
        self.in_sigma = -1                      # 内部连通量的影响范围
        self.out_sigma = -1                     # 外部影响范围
        self.decay = 1                          # 考虑到被种子节点影响的衰减

    def add_in_child(self, v, w):
        if v not in self.in_children:
            self.in_children[v] = (1 - w)
        else:
            self.in_children[v] *= (1 - w)
        
    
    def add_out_children(self, sc, w, force=False):

        if sc not in self.out_children or force:
            self.out_children[sc] = (1 - w)
        else:
            self.out_children[sc] *= (1 - w)               # 指向同一个分量可能有好几条边

        
    
    def add_father(self, v, w):
        self.father[v] = w                      # 在计算完之后添加父亲，这时边的权重已经确定
    
    def get_in_children_sigma(self, forest: dict, force=False):
        if self.in_sigma == -1 or force:
            if self.v in self.in_children:
                temp = self.in_children[self.v][1]
            else:
                temp = 1
            
            for v, w in self.in_children.items():
                if v == self.v:
                    continue
                temp += (1 - w[0]) * forest[v].get_out_children_sigma(forest)
            self.in_sigma = temp
        return self.decay * self.in_sigma
    
    def get_out_children_sigma(self, forest: dict, force=False):
        if self.out_sigma == -1 or force:
            temp = 0
            for v, w in self.out_children.items():
                temp += (1 - w) * forest[v].get_in_children_sigma(forest)
            self.out_sigma = temp
        return self.decay * self.out_sigma


    def get_sigma(self, forest: dict, force=False):
        sigma = self.get_in_children_sigma(forest, force)
        sigma += self.get_out_children_sigma(forest, force)

        return sigma
    
    def remove_child_sigma(self, node):
        decay = self.out_children[node.v]
        for v, w in node.out_children.items():
            self.out_children[v] /= (w * decay)
    
    def format_in_children(self):
        print("[", end="")
        for v, w in self.in_children.items():
            print(v, ":", round(w, 4), ",", end="")
        print("]")

class ActiveEdge:
    def __init__(self):
        self.e = {}
    
    def add_link(self, v, w):
        if v not in self.e:
            self.e[v] = (1 - w)
        else:
            self.e[v] *= (1 - w)
    
    def remove(self, v):
        if v in self.e:
            del self.e[v]
    
@fn_timer
def zmd_node_select(k: int, g: ZGraph, rg: ZGraph, retForest=False):

    scc, scc_group = construct_strong_connect_componet(g)  # 构建强连通分量

    forest: Dict[int, ZMDTree] = {}             # 用来保存缩点后的森林

    for u in g.network.keys():
        forest[u] = ZMDTree(u, scc[u])
    

    construct_inner(g, forest, scc)
    # construct_inner_slow(g, forest, scc)
    construct_out_more(g, forest, scc)
    # construce_out(g, forest, scc)
      
    Q = []
    for u in g.get_network_candidates():
        ancestor = forest[u]
        sigma = ancestor.get_sigma(forest)
        Q.append([sigma, u, ancestor])
    
    if retForest:
        return Q

    Q = sorted(Q, key=lambda x: x[0], reverse=True)

    debug_node_idx = -1

    for _, item in enumerate(Q):
        sigma, u, ancestor = item
        if u != debug_node_idx:
            continue
        print(sigma)
        count_sigma_in_random_networks([u], g, forest[u])
    
    Seed = []
    PredictSigma = 0
    for i in range(k):
        sigma, seed = Q[0][0], Q[0][1]
    
        for v, w in forest[seed].out_children.items():
            forest[v].decay = max(0, forest[v].decay - (1 - w))
            forest[v].get_sigma(forest, True)

        for v,w in forest[seed].father.items():
            forest[v].remove_child_sigma(forest[seed])
            forest[v].get_sigma(forest, True)

        for v, w in forest[seed].in_children.items():
            forest[v].decay = max(0, forest[v].decay - (1 - w[0]))
        
        for v in scc_group[forest[seed].sc]:
            if seed in forest[v].in_children:
                target = forest[v].in_children[seed]
                forest[v].in_children[v][1] -= (1 - target[0]) * target[1]
            forest[v].get_sigma(forest, True)
        
        Seed.append(seed)
        PredictSigma += sigma

        Q = Q[1:]
        for i in range(len(Q)):
            Q[i][0] = Q[i][2].get_sigma(forest)
        Q = sorted(Q, key=lambda x: x[0], reverse=True)

    if debug_node_idx > -1:
        print(forest[debug_node_idx].get_in_children_sigma(forest))
        print(forest[debug_node_idx].get_out_children_sigma(forest))
        draw_one_node_with_out_children(forest[debug_node_idx])
    
    print(PredictSigma)
    return Seed

def construct_strong_connect_componet(g: ZGraph):
    n = g.max_v + 1
    dfn = [-1 for i in range(n)]
    low = [-1 for i in range(n)]
    in_statck = [False for i in range(n)]
    dfncnt = 0

    sc = 0                                      # 强连通量的个数
    scc = [-1 for i in range(n)]                # 用来保存强连通分量的编号
    scc_group = {}

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
            scc_group[sc] = [u]
            while stack[tp] != u:
                scc[stack[tp]] = sc
                scc_group[sc].append(stack[tp])
                in_statck[stack[tp]] = False
                tp -= 1
            
            scc[u] = sc
            in_statck[u] = False
            tp -= 1
            sc += 1

    
    for u in g.network.keys():
        if dfn[u] == -1:
            tarjan(u)
    
    logging.debug("构建了{}个强连通分量".format(sc))

    return scc, scc_group

def construct_inner(g: ZGraph, forest: Dict[int, ZMDTree], scc: List[int]):
    
    visited = dict()
    
    def in_dfs(root: int, path: deque, decay=1) -> dict:
        if root in visited:
            return visited[root]
        
        ret = {root: [0, 1]}

        if decay < 10 ** (-4):
            return ret
        
        root_sigma = 1
        
        for v in g.get_neighbors_keys(root):
            if scc[v] != scc[root] or v in path:
                continue
            
            #　w 激活概率
            w = g.network[root][v]
            path.append(v)
            jump_arrive = in_dfs(v, path, w * decay)

            # jump_w 没有激活概率
            for jump_v, jump_w in jump_arrive.items():
                r_w = 1 - (1 - jump_w[0]) * w
                if jump_v in ret:
                    root_sigma -= (1 - ret[jump_v][0])
                    ret[jump_v][0] *= r_w
                    root_sigma += (1 - ret[jump_v][0])
                else:
                    ret[jump_v] = [r_w, jump_w[1]]
                    root_sigma += (1 - r_w)
            path.pop()
        
        ret[root][1] = root_sigma
        visited[root] = ret

        return ret
    
    for u in g.get_network_candidates():
        ancestor = forest[u]
        visited.clear()
        arrived = in_dfs(u, deque([u]))
        ancestor.in_children = arrived.copy()
    
    logging.debug("完成了连通分量内部的构造")
    

def construct_inner_slow(g: ZGraph, forest: Dict[int, ZMDTree], scc: List[int]):
    visited=dict()
    def in_dfs(root: int, path=[], decay = 1) -> ActiveEdge:
        if root in visited:
            return visited[root]
        
        arrived = ActiveEdge()
        if decay < 10 ** (-4):
            return arrived
        
        for v in g.get_neighbors_keys(root):
            if scc[v] != scc[root]:
                continue
            
            w = g.network[root][v]
            arrived.add_link(v, w)
            if v in path:
                continue
            path.append(v)
            jump_arrive: ActiveEdge = in_dfs(v, path, w * decay)
            path.pop()
            for jump_v, jump_w in jump_arrive.e.items():
                if jump_v == root:
                    continue
                arrived.add_link(jump_v, w * (1 - jump_w))
        visited[root] = arrived
        return arrived
            
    # 构造强连通分量内部的连接
    for u in g.get_network_candidates():
        ancestor = forest[u]
        visited.clear()
        arrived = in_dfs(u, [u])
        arrived.remove(u)
        ancestor.in_children = arrived.e.copy()
        # logging.debug("节点{}完成内部连接".format(u))

    logging.debug("完成了连通分量内部的构造")


def construct_out_more(g: ZGraph, forest: Dict[int, ZMDTree], scc: List[int]):
    
    count_edges = dict()

    def count_edge(root: int) -> Counter:
        if root in count_edges:
            return count_edges[root]

        edges = set()

        for v in g.get_neighbors_keys(root):
            if scc[v] == scc[root]:
                continue
            
            edges.add((root, v))
            edges.update(count_edge(v))
            
        count_edges[root] = edges

        return count_edges[root]
    
    def dfs(root: int) -> Counter:
        c = Counter()
        for edge in count_edges[root]:
            c[edge[1]] += 1
        
        if forest[root].has_visited_out:
            return 
        
        for v in g.get_neighbors_keys(root):
            if scc[v] == scc[root]:
                continue
            
            c[v] -= 1

            decay = g.network[root][v]
            forest[root].add_out_children(v, decay)

            dfs(v)

            q = [v] if c[v] == 0 else None

            while q:
                cur = q.pop()
                decay = 1 - forest[root].out_children[cur]
            
                for k, w in g.network[cur].items():

                    if scc[k] == scc[v]:
                        continue
                    forest[root].add_out_children(k, decay * w)
                    c[k] -= 1
                    if c[k] == 0:
                        q.append(k)
        
        for v, w in forest[root].out_children.items():
            forest[v].add_father(root, 1-w)

        forest[root].has_visited_out = True
            
    # 构造强连通分量之间的连接 
    for u in g.get_network_candidates():
        count_edge(u)

    for u in g.get_network_candidates():
        ancestor = forest[u]
        if ancestor.has_visited_out:
            continue
        dfs(u)
    
    logging.debug("完成了连通分量外部的构造")


def construce_out(g: ZGraph, forest: Dict[int, ZMDTree], scc: List[int]):
    
    def out_dfs(root: int):

        if forest[root].has_visited_out:
            return
        
        for v in g.get_neighbors_keys(root):
            if scc[v] == scc[root]:
                continue
            
            out_dfs(v)

            decay = g.network[root][v]
            # if root == 48:
            #     print(forest[root].out_children)

            forest[root].add_out_children(v, decay)

            for u, w in forest[v].out_children.items():
                forest[root].add_out_children(u, decay * (1 - w))

        for v, w in forest[root].out_children.items():
            forest[v].add_father(root, 1-w)
            
        forest[root].has_visited_out = True
            

    # 构造强连通分量之间的连接  
    for u in g.get_network_candidates():
        ancestor = forest[u]
        if ancestor.has_visited_out:
            continue
        out_dfs(u)
    
    logging.debug("完成了连通分量外部的构造")

def draw_one_node_with_out_children(node: ZMDTree):
    if len(node.out_children.keys()) > 100:
        return

    import pygraphviz as pgv

    g = pgv.AGraph(directed=True)

    out_children = node.out_children.copy()
    out_children = sorted(out_children.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    for v, w in out_children:
        g.add_edge(node.v, v, label=str(round(1-w, 3)))
    
    g.layout(prog='dot') # use dot
    g.draw('out.png', prog="dot")


def draw_one_node_with_in_children(node: ZMDTree):
    if len(node.out_children.keys()) > 100:
        return

    import pygraphviz as pgv
    
    g = pgv.AGraph(directed=True)

    for v, w in node.in_children.items():
        g.add_edge(node.v, v, label=str(round(1-w, 3)))
    
    g.layout(prog='dot') # use dot
    g.draw('in.png', prog="dot")