
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

mpl.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 1

import logging

def draw_sigma(network):

    csv = pd.read_csv('./Test/{}.csv'.format(network), index_col=0, header=0)
    algs = csv.index.tolist()
    # ['CELF++', 'MaxDegree', 'TIM', 'StaticGreedy', 'ICT']
    draw_config = {
        'CELF++': ['#1B9D77', 'p'],
        'MaxDegree': ['#A6CFE3', 's'],
        'TIM': ['#EF8860', 'v'],
        'StaticGreedy': ['#A2A2A2', '^'],
        'ICT': ['#386BB0', 'o']
    }

    plt.figure(figsize=(10,8))
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    x = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 48]
    for alg in algs:
        data = csv.loc[alg]
        data = [data[i] for i in x]
        arr = x[:]
        arr[0] = 1
        plt.plot(arr, data, label=alg, color=draw_config[alg][0], marker=draw_config[alg][1], linewidth=2.5, markersize=10)
    
    ax.set_ylabel('Spread of influence', labelpad=5, size=18)
    ax.set_xlabel('Number of seeds(k)', labelpad=10, size=18)
    plt.legend()

    plt.savefig('D:\latexProject\CSCWD\DrawMax\sigma-{}.pdf'.format(network), dpi=300, transparent=False, bbox_inches='tight')


if __name__ == "__main__":
    draw_sigma('NetPHYFix')