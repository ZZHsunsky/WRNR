'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-13 08:59:59
LastEditors: zehao zhao
LastEditTime: 2020-10-13 09:46:02
'''
import sys
from zutils import *
from zatim import tim_node_selection
from zacelf import celf_in_origin_network
from zacelf import  max_degree_in_origin_network
from zaviolence import violence_in_sub_networks
from zatdc import tdc_node_selection
from zatdc import tdc_with_scc
from zazmd import zmd_node_select
import logging

import networkx as nx
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Random network NetHEPTFix NetPHYFix
    # network_type = 'network'
    # k = 5
    # mc = 10000

    # # 加载原生图
    original_network = ZGraph()
    load_network(original_network, 'test')
    zmd_node_select(original_network)

    
    # G = nx.Graph()
    # G.add_node(1)
    # G.add_edge(2, 3)
    # # G.add_edge(3, 2)
    # print("输出全部节点：{}".format(G.nodes()))
    # print("输出全部边：{}".format(G.edges()))
    # print("输出全部边的数量：{}".format(G.number_of_edges()))
    # nx.draw(G)
    # plt.show()