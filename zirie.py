from zutils import *
from matplotlib import pyplot as plt
import scipy.sparse as sparse
import torch
from scipy import stats

cost = {}

@fn_timer
def IRIE(k: int, g: ZGraph, sp_a: coo_matrix, func):
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

def draw_simulate_predict(n: int, g: ZGraph, X, Y, func):

    xlength = min(n, 50)
    simulate = []
    cost_simulate = []
    for i in range(xlength):
        # simulate.append(calc_sigma_in_random_networks([i], g))
        sigma, reward = calc_sigma_in_networks_with_cost([i], g, func=func)
        simulate.append(sigma)
        cost_simulate.append(reward)

    predict = X.ravel().tolist()[:xlength]
    cost_predict = Y.ravel().tolist()[:xlength]
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

    ax.set_ylabel('Expected Influence', labelpad=10)

    plt.plot(x, simulate, marker='o', label="simulate", color="#3451AC", linewidth=1.5)
    plt.plot(x, predict, marker='*', label="predict", color="#EB222B", linewidth=1.5)
    plt.legend()


    # 画期望代价
    plt.subplot(212)
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    ax.set_xlabel('User ID', labelpad=5)
    ax.set_ylabel('Expected Cost', labelpad=10)

    plt.plot(x, cost_simulate, marker='o', label="simulate", color="#3451AC", linewidth=1.5)
    plt.plot(x, cost_predict, marker='*', label="predict", color="#EB222B", linewidth=1.5)
    plt.legend()

    plt.show()

