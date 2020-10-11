'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-25 10:18:27
LastEditors: zehao zhao
LastEditTime: 2020-10-10 11:29:30
'''
from zutils import *
from zclass import ZBitGraph, TreeNode
import logging

@fn_timer
def tdc_node_selection(k: int, g: ZGraph, mc=1000):
    candidates = g.get_network_candidates()
    if k >= len(candidates):
        return candidates
    
    Seed = []
    pbar = tqdm(total=100)
    for _ in range(mc):
        if  _ % (mc // 10) == 0:
            pbar.update(10)
        Seed.extend(bit_graph_selection(k, g,))
    pbar.close()

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
        #         logging.debug(key, bin(v))

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

@fn_timer
def tdc_with_scc(k: int, g: ZGraph, mc=1000) -> List[int]:
    Seed = []
    pbar = tqdm(total=100)
    for _ in range(mc):
        if  _ % (mc // 10) == 0:
            pbar.update(10)
        Seed += constrouct_scc_forest(k, g)
    pbar.close()
    
    C = Counter(Seed)
    return [x[0] for x in C.most_common(k)]

def constrouct_scc_forest(k: int, g: ZGraph) -> List[int]:
    n = g.max_v + 1
    dfn = [-1 for i in range(n)]
    low = [-1 for i in range(n)]
    in_statck = [False for i in range(n)]
    dfncnt = 0

    sc = 0 # 强连通量的个数
    scc = [-1 for i in range(n)] # 用来保存强连通分量的编号
    sccd = {}

    forest: Dict[int, TreeNode] = {} # 用来保存缩点后的森林

    stack = [-1 for i in range(n)]
    tp = 0 # 表示栈顶
    temp_network = {}
    def tarjan(u):
        nonlocal dfn, low, dfncnt, scc, sc, tp

        low[u] = dfn[u] = dfncnt
        dfncnt += 1

        tp += 1
        stack[tp] = u

        in_statck[u] = True
        neighbors = g.get_neighbors_keys_with_w(u)
        temp_network[u] = neighbors

        for v in neighbors:
            if dfn[v] == -1:
                tarjan(v)
                low[u] = min(low[u], low[v])
            elif in_statck[v]:
                low[u] = min(low[u], dfn[v])
        
        if dfn[u] == low[u]:
            temp_component = [u]
            while stack[tp] != u:
                temp_component.append(stack[tp])
                scc[stack[tp]] = sc
                in_statck[stack[tp]] = False
                tp -= 1
                
            scc[u] = sc
            in_statck[u] = False
            tp -= 1
            sccd[sc] = temp_component
            forest[sc] = TreeNode(sc, len(temp_component))
            sc += 1

    
    for u in g.get_network_candidates():
        if dfn[u] == -1:
            tarjan(u)
    
    logging.debug("构建了强连通分量")
    is_roots = [True for i in range(sc)]
    # 构建缩点之后的森林
    for u in g.get_network_candidates():
        for v in temp_network[u]:
            if scc[u] == scc[v]:
                continue

            forest[scc[u]].add_child(forest[scc[v]])
            is_roots[scc[v]] = False
    
    roots_idx = [_ for (_, i) in enumerate(is_roots) if i]
    roots = [forest[i] for i in roots_idx]
    logging.debug("构建了树")

    bulil_two_level_tree(forest, roots_idx)
    logging.debug("构建了两级树")


    k_scc = pick_k_scc_from_foreast(k, roots)
    logging.debug("选择了k个分量")
    k_nodes = []
    for sc_idx in k_scc:
        k_nodes += sccd[sc_idx]
    
    return k_nodes

def bulil_two_level_tree(forest: Dict[int, TreeNode], roots: List[bool]):

    def get_subtree(root: TreeNode):
        if root.get_sub:
            return root.children.copy()
        
        sub_tree = root.children.copy()

        for child in root.children.values():
            sub_tree.update(get_subtree(child))

        root.children = sub_tree
        root.get_sub = True
        return sub_tree

    for root_idx in roots:
        root = forest[root_idx]
        get_subtree(root)

    for root_idx in roots:
        root = forest[root_idx]
        for child in root.children.values():
            root.w += child.w
            child.children = None
            child.set_father(root)


def pick_k_scc_from_foreast(k: int, roots: List[TreeNode]):
    k_scc = []
    top_scc = []
    
    def discount_father_w(root: TreeNode, w=0):
        for father in root.fathers.values():
            father.w -= root.w

    for i in range(k):
        roots.sort(key=lambda node: node.w, reverse=True)
        top = roots[0]
        # 加入subw最大的
        k_scc.append(top.v)

        for child in top.children.values():
            discount_father_w(child)
        
        roots = roots[1:]

    return k_scc

def judge_tree_has_cycel(root: TreeNode) -> bool:
    visited = set()

    def dfs(root: TreeNode):
        print(root.v)
        ret = False
        
        if root.v in visited:
            print(visited, root.v)
            return True
        
        visited.add(root.v)
        
        for child in root.children.values():
            ret = ret or dfs(child)
        
        return ret
    
    return dfs(root)