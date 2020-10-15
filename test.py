'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-13 08:59:59
LastEditors: zehao zhao
LastEditTime: 2020-10-15 18:10:30
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

logging.basicConfig(level=logging.INFO)
sys.setrecursionlimit(200000)

if __name__ == "__main__":
    
    # Random network NetHEPTFix NetPHYFix

    k = 1
    mc = 1000


    # 加载原生图
    g = ZGraph()
    load_network(g, 'test')
    # g.draw_with_networkx()

    zmd_seed = zmd_node_select(k, g)
    calc_sigma_in_random_networks(zmd_seed, g, mc)

    # g = ZGraph()
    # load_network(g, 'network')
    # zmd_seed = zmd_node_select(k, g)
    # calc_sigma_in_random_networks(zmd_seed, g, mc)

    # g = ZGraph()
    # load_network(g, 'NetHEPTFix')
    # zmd_seed = zmd_node_select(k, g)
    # calc_sigma_in_random_networks(zmd_seed, g, mc)
