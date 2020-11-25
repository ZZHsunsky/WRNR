
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from collections import defaultdict
import numpy as np
from zutils import *
from zcostfunc import *
from zirie import IRIE

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

    plt.figure(figsize=(10,7))
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    x = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 48]
    for alg in draw_config.keys():
        if alg not in algs:
            continue
        
        data = csv.loc[alg].tolist()
        arr = x[:]

        if len(data) == 10:
            arr.pop(0)
        else:
            data = [data[i] for i in x]
            arr[0] = 1

        plt.plot(arr, data, label=alg, color=draw_config[alg][0], marker=draw_config[alg][1], linewidth=2.5, markersize=10)
    
    plt.yticks(size=18)
    plt.xticks(size=18)

    ax.set_ylabel('Spread of influence', labelpad=5, size=20)
    ax.set_xlabel('Number of seeds(k)', labelpad=10, size=20)
    plt.legend(fontsize=18)

    plt.savefig('D:\latexProject\CSCWD\DrawMax\sigma-{}.pdf'.format(network), dpi=300, transparent=False, bbox_inches='tight')

def draw_runtime():
    file = open('./Test/runtime.csv', 'r')
    datasets = ['NetHEPT', 'NetPHY', 'Sina Weibo']
    record = defaultdict(list)
    bar_width = 3

    draw_config = {
        'MaxDegree': ['#9ABBF3', '/'],
        'StaticGreedy': ['#FFFFA2', 'x'],
        'CELF++': ['#C2B2D6', '-'],
        'TIM': ['#9BD59B', "\\"],
        'ICT': ['#FDC897', None]
    }

    for line in file.readlines():
        arr = line.strip().split(',')
        alg, val = arr[0], float(arr[1])
        record[alg].append(val)
    
    for alg in record.keys():
        while len(record[alg]) < len(datasets):
            record[alg].append(10**-9)
    
    x = np.array([i * 15 + i * 10 for i in range(3)])
    idx = 0
    plt.figure(figsize=(22,14))
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    # ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
    # ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    # 显示高度
    def autolabel(rects, labels):
        for rect, label in zip(rects, labels):
            height = rect.get_height()
            if height == 0:
                continue
            plt.text(rect.get_x() - 0.3, 0.1 + height, label, fontsize=20, zorder=11)

    for alg in record.keys():
        data = np.array(record[alg])
        height_label = []
        for d in data:
            cnt = 0
            while d >= 60:
                d /= 60
                cnt += 1
            unit = 's'
            if cnt == 1:
                unit = 'm'
            elif cnt == 2:
                unit = 'h'
            if d < 0.01:
                label = str(round(d, 3)) + unit
            elif d < 10:
                label = str(round(d, 2)) + unit
            else:
                label = str(round(d, 1)) + unit
            
            height_label.append(label)
        data = np.log10(data) + 3
        data = np.clip(data, 0, 10)
        autolabel(plt.bar(x + idx * bar_width, data, bar_width, label=alg, color=draw_config[alg][0], hatch=draw_config[alg][1],edgecolor='#000000', zorder=10), height_label)
        idx += 1

    y = np.array([i for i in range(-3, 7, 2)])

    ytick = [r'$10^{'+ str(i) +'}$' for i in y]

    plt.xticks(x + bar_width * 5 / 2, datasets, size=28)
    plt.yticks(y + 3, ytick, size=28)

    plt.ylabel('Running time(s)', labelpad=5, size=32)
    plt.xlabel('Datasets', labelpad=10, size=32)

    # plt.legend(ncol=2, loc=2, fontsize=28, shadow=False, fancybox=False)
    plt.legend(fontsize=28)
    # plt.show()
    plt.savefig('D:\latexProject\CSCWD\DrawMax\Runtime.pdf', dpi=300, transparent=False, bbox_inches='tight')

def draw_simulate_predict():
    k = 1
    mc = 1000

    network_type = "NetHEPTFix"

    # 加载原生图

    g = ZGraph()
    sp_a = load_network(g, network_type)

    func = sigmod_func
    IRIE(k, g, sp_a, func, True)


def draw_cost(network):
    import os
    name = network

    if name == 'EpinionsFix':
        name = "NetPHYFix"

    if not os.path.exists('./Test/Cost-{}.csv'.format(name)):
        print(name, "COST 记录不存在")
        return
    file = open('./Test/Cost-{}.csv'.format(name), 'r')
    record = {}

    xlenth = 0
    for line in file.readlines():
        arr = line.split(',')
        alg = arr.pop(0)
        sigmas = list(map(lambda x: float(x), arr))
        xlenth = len(sigmas)
        record[alg] = sigmas

    bar_width = 3
    x = np.array([i * bar_width * 6  for i in range(xlenth)])

    draw_config = {
        'MaxDegree': ['#9ABBF3', '/'],
        'StaticGreedy': ['#FFFFA2', 'x'],
        'CELF++': ['#C2B2D6', '.'],
        'TIM': ['#9BD59B', "\\"],
        'ICT': ['#FDC897', None]
    }

    plt.figure(figsize=(22,14))
    plt.grid(linestyle="--")  # 设置背景网格线为虚线
    ax = plt.gca()
    
    ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
    ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

    idx = 0
    for alg in draw_config.keys():
        if alg not in record:
            continue
        plt.bar(x + idx * bar_width, record[alg], bar_width, label=alg, zorder=10, color=draw_config[alg][0], hatch=draw_config[alg][1], edgecolor='#000000')
        idx += 1

    plt.yticks(size=40)
    plt.xticks(x + bar_width * 5 / 2.5, budgets_config[network], size=40)

    ax.set_ylabel('Spread of influence', labelpad=5, size=48)
    ax.set_xlabel('Budget', labelpad=10, size=48) 
    plt.legend(fontsize=40)
    plt.savefig('D:\latexProject\CSCWD\DrawMax\Cost-{}.pdf'.format(network), dpi=300, transparent=False, bbox_inches='tight')


if __name__ == "__main__":
   
    draw_runtime()
    # draw_simulate_predict()
    networks = ['NetHEPTFix', 'NetPHYFix', 'EpinionsFix']

    for network in networks:
        draw_sigma(network)
        draw_cost(network)