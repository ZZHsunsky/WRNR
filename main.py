'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-14 18:24:34
LastEditors: zehao zhao
LastEditTime: 2020-10-16 19:27:59
'''
import sys
from zutils import *
from zcostfunc import * 
from zatim import tim_node_selection
from zacelf import celf_in_origin_network
from zacelf import  max_degree_in_origin_network
from zaviolence import violence_in_sub_networks
from zatdc import tdc_node_selection
from zatdc import tdc_with_scc
from zazmd import zmd_node_select
import logging

logging.basicConfig(level=logging.DEBUG)
sys.setrecursionlimit(200000)

if __name__ == "__main__":
    # Random network NetHEPTFix NetPHYFix
    network_type = 'NetHEPTFix'
    k = 20
    mc = 1000


    # 加载原生图
    original_network = ZGraph()
    load_network(original_network, network_type)

    reverse_network = ZGraph()
    load_network(reverse_network, network_type, reverse=True)

    original_network.draw_with_networkx()
    # CELF
    # celf_seed = celf_in_origin_network(k, original_network, mc=mc)
    # calc_sigma_in_random_networks(celf_seed, original_network, mc)

    func = slow_fast_increase
    with_cost = False

    # max degree
    max_degree_seed = max_degree_in_origin_network(k, original_network)
    if with_cost:
        calc_sigma_in_networks_with_cost(max_degree_seed,  original_network, mc, func)
    else:
        calc_sigma_in_random_networks(max_degree_seed, original_network, mc)

    # ris 

    ris_seed = tim_node_selection(k, reverse_network, mc * 100)
    if with_cost:
        calc_sigma_in_networks_with_cost(ris_seed, original_network, mc, func)
    else:
        calc_sigma_in_random_networks(ris_seed, original_network, mc)

    # tdc
    # tdc_seed = tdc_with_scc(k, original_network, mc)
    # calc_sigma_in_random_networks(tdc_seed, original_network, mc)

    # zmd
    zmd_seed = zmd_node_select(k, original_network, reverse_network)
    if with_cost:
        calc_sigma_in_networks_with_cost(zmd_seed, original_network, mc, func)
    else:
        calc_sigma_in_random_networks(zmd_seed, original_network, mc)
    print("")
