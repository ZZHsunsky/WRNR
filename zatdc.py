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
        neighbors = g.get_neighbors_keys(u)
        temp_network[u] = neighbors

        for v in neighbors:
            if dfn[v] == -1:
                tarjan(v)
                low[u] = min(low[u], low[v])
            elif in_statck[v]:
                low[u] = min(low[u], dfn[v])
        
        if dfn[u] == low[u]:
            sc += 1
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
    
    for u in g.get_network_candidates():
        if dfn[u] == -1:
            tarjan(u)
    
    print("共有强连通量：", sc)
    print("共有节点：", g.max_v)

    # 构建缩点之后的森林
    for u in g.get_network_candidates():
        for v in temp_network[u]:
            if scc[u] == scc[v]:
                continue

            forest[scc[u]].add_child(forest[scc[v]])
    
    max_w, max_scc_idx = -1, -1

    def dfs(node: TreeNode):
        if node.subW > 0:
            return node.subW

        node.subW = w

        for child in node.children:
            node.subW += dfs(child)

        return node.subW
    
    for scc_idx, node in forest.items():
        temp_w = dfs(node)
        if max_w < temp_w:
            max_w, max_scc_idx = temp_w, scc_idx
         