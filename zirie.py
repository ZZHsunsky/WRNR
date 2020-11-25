from zutils import *
from matplotlib import pyplot as plt
import scipy.sparse as sparse
from scipy import stats
import heapq

cost = {}
ap = defaultdict(int)

@fn_timer
def IRIE(k: int, g: ZGraph, sp_a: coo_matrix, func, debug=False):
    n = g.max_v + 1


    s, sigma = compute_influcen_cost(g, [], func, debug)
    Seed = [s]
    for i in range(1, k):
        for j in range(n):
            ap[j] = 0
        
        compute_ap(g, Seed)
        s, v = compute_influcen_cost(g, [], func)
        sigma += v
        Seed.append(s)

    return Seed

def compute_ap(g: ZGraph, Seed: List[int]):
    threshold = math.log(320)
    tempAp = [float('inf') for i in range(g.max_v + 1)]

    q = []
    for s in Seed:
        tempAp[s] = 0
        ap[s] = 1
        q.append((0, s))

    while q:
        dist, u = heapq.heappop(q)

        if dist > threshold:
            break
        
        if u not in g.network:
            continue
        
        for k, w in g.network[u].items():
            if tempAp[k] > dist + w:
                tempAp[k] = dist + w
                heapq.heappush(q, (dist + w, k))

        ap[u] += math.exp(-dist)
        ap[u] = min(ap[u], 1)


def compute_influcen_cost(g: ZGraph, Seed: Set, func, debug=False) -> int:
    n = g.max_v + 1

    dp = [1 - ap[i] for i in range(n)]
    ndp = [0 for i in range(n)]

    C = []
    candi = g.get_network_candidates()

    for i in range(n):
        C.append(calc_active_number_distribute(g.get_neighbors_count(i), func))
    costdp = C[:]
    ncostdp = [0 for i in range(n)]

    for i in range(10):
        for u in candi:
            ndp[u] = 1
            ncostdp[u] = 0
            for k, w in g.network[u].items():
                ndp[u] += w * dp[k]
                ncostdp[u] += w * costdp[k]
            ndp[u] *= (1 - ap[u])
            ncostdp[u] += C[u]
        
        for u in candi:
            dp[u] = ndp[u]
            costdp[u] = ncostdp[u]
    
    if debug:
        arr = np.array(dp)
        top_k_idx = arr.argsort()[::-1][:10]
        draw_simulate_predict(n, g, dp, costdp, func, [])
    
    return get_max_idx(dp)


def irie_with_matrix(k: int, g: ZGraph, sp_a: coo_matrix, func):
    n = g.max_v + 1

    C = []
    for i in range(n):
        C.append(calc_active_number_distribute(g.get_neighbors_count(i), func))
    
    # C保存激活自身的代价
    C = np.array(C)  
    C.reshape((n, 1))
    # Y表示级联后的代价
    Y = C.copy()

    # MA表示概率矩阵
    MA  = sp_a.copy()

    # B表示激活自身
    B = np.ones((n, 1))
    # X表示级联后，激活节点的期望值
    X = np.ones((n, 1))

    for i in range(10):
        Y += MA.dot(C)
        X += MA.dot(B)
        MA = MA.dot(sp_a)    

    draw_simulate_predict(n, g, X, Y, func)

def calc_active_number_distribute(n, func):
    if n in cost:
        return cost[n]
    
    probablity = stats.binom.pmf(np.arange(n+1), p=0.1, n=n)
    temp = 0

    for i in range(len(probablity)):
        temp += probablity[i] * func(i)
    cost[n] = temp
    return cost[n]

def get_max_idx(arr: List):
    if len(arr) == 0:
        return -1
    
    max_value = arr[0]
    max_idx = 0

    for i in range(1, len(arr)):
        if arr[i] > max_value:
            max_idx, max_value = i, arr[i]
    return max_idx, max_value

def draw_simulate_predict(n: int, g: ZGraph, X, Y, func, x = []):

    if len(x) == 0:
        xlength = min(n, 50)
        x = [i for i in range(xlength)]
    else:
        x.sort()
        xlength = len(x)
    
    simulate = []
    cost_simulate = []


    for i in x:
        # simulate.append(calc_sigma_in_random_networks([i], g))
        sigma, reward = calc_sigma_in_networks_with_cost([i], g, func=func)
        simulate.append(sigma)
        cost_simulate.append(reward)

    if type(X) != list:
        X = X.ravel().tolist()
    if type(Y) != list:
        Y = Y.ravel().tolist()

    predict = []
    cost_predict = []

    for i in x:
        predict.append(X[i])
        cost_predict.append(Y[i])

    x = [i for i in range(xlength)]
    plt.figure(figsize=(12,8))
    
    # 画期望活跃节点
    plt.subplot(211)
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    ax.set_ylabel('Expected Influence', labelpad=10, size=18)

    plt.plot(x, simulate, marker='o', label="simulate", color="#3451AC", linewidth=1.5)
    plt.plot(x, predict, marker='*', label="predict", color="#EB222B", linewidth=1.5)
    plt.legend(fontsize=18)


    # 画期望代价
    plt.subplot(212)
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    ax.set_xlabel('User ID', labelpad=5, size=18)
    ax.set_ylabel('Expected Cost', labelpad=10, size=18)

    plt.plot(x, cost_simulate, marker='o', label="simulate", color="#3451AC", linewidth=1.5)
    plt.plot(x, cost_predict, marker='*', label="predict", color="#EB222B", linewidth=1.5)
    plt.legend(fontsize=18)
    plt.savefig('D:\latexProject\CSCWD\DrawMax\sigma-predict.pdf', dpi=300, transparent=False, bbox_inches='tight')


