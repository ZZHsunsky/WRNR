import sys
from zutils import *
from zatim import tim_node_selection
from zacelf import celf_in_origin_network
from zacelf import  max_degree_in_origin_network
from zaviolence import violence_in_sub_networks
from zatdc import tdc_node_selection
from zatdc import tdc_with_scc
from zazmd import zmd_node_select
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 1

import logging

logging.basicConfig(level=logging.INFO)
sys.setrecursionlimit(200000)

if __name__ == "__main__":
    # Random network NetHEPTFix NetPHYFix
    network_type = 'NetPHYFix'
    k = 1
    mc = 1000

    # 加载原生图
    original_network = ZGraph()
    load_network(original_network, network_type)

    reverse_network = ZGraph()
    load_network(reverse_network, network_type, reverse=True)

    Q = zmd_node_select(k, original_network, reverse_network, retForest=True)

    simulate = []
    predict = []
    xlength = 50
    x = []

    for _, item in enumerate(Q):
        if _ > xlength:
            break
        x.append(_+1)
        sigma, u, ancestor = item
        predict.append(sigma)
        simulate.append(calc_sigma_in_random_networks([u], original_network))

    plt.figure(figsize=(9,5))
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    ax.set_xlabel('User ID', labelpad=5)
    ax.set_ylabel('Expected Influence', labelpad=10)

    plt.plot(x, simulate, marker='o', label="simulate", color="#3451AC", linewidth=1.5)
    plt.plot(x, predict, marker='*', label="predict", color="#EB222B", linewidth=1.5)

    plt.legend()

    plt.savefig('D:\latexProject\CSCWD\DrawMax\sigma-predict.pdf', dpi=300, transparent=False, bbox_inches='tight')
    plt.show()