'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-14 18:24:34
LastEditors: zehao zhao
LastEditTime: 2020-10-12 17:48:21
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
    network_type = 'NetHEPTFix'
    k = 1
    mc = 1000


    # 加载原生图
    original_network = ZGraph()
    load_network(original_network, network_type)
    
    seed = zmd_node_select(original_network)
    calc_sigma_in_random_networks(seed, original_network, mc)

    # violence
    # seed = violence_in_sub_networks(k, original_network)     #[56, 58, 53]
    # print(blue_print("[Cache] ") + green_print("VIOLENCE_IN_SUB_NETWORKS ") + orange_print("0.0 ") + "Seconds")


    # CELF
    celf_seed = celf_in_origin_network(k, original_network, mc=mc)
    calc_sigma_in_random_networks(celf_seed, original_network, mc)

    # max degree
    max_degree_seed = max_degree_in_origin_network(k, original_network)
    calc_sigma_in_random_networks(max_degree_seed,  original_network, mc)

    # ris 
    reverse_network = ZGraph()
    load_network(reverse_network, network_type, reverse=True)
    ris_seed = tim_node_selection(k, reverse_network, mc * 100)
    calc_sigma_in_random_networks(ris_seed,  original_network, mc)

    # #tdc
    # tdc_seed = tdc_node_selection(k, original_network, mc)
    # time.sleep(1)
    # calc_sigma_in_random_networks(tdc_seed, original_network, mc)
    # print("")
    # tdc_seed = tdc_with_scc(k, original_network, mc)
    # calc_sigma_in_random_networks(tdc_seed, original_network, mc)
    # print("")
