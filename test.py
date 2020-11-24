'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-13 08:59:59
LastEditors: zehao zhao
LastEditTime: 2020-10-16 19:06:42
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
from zirie import IRIE
import logging

logging.basicConfig(level=logging.INFO)
sys.setrecursionlimit(200000)


if __name__ == "__main__":
    
    # Random network NetHEPTFix NetPHYFix EpinionsFix


    k = 50
    mc = 1000

    network_type = "NetHEPTFix"

    # 加载原生图
    original_network = ZGraph()
    sp_a = load_network(original_network, network_type)


    # zmd_seed = zmd_node_select(k, g, None)
    # calc_sigma_in_networks_with_cost(zmd_seed, g, mc, linear_increase)
    func = slow_fast_increase
    irie_seed = IRIE(k,original_network, sp_a, func)
    if k > 1:
        calc_sigma_in_networks_with_cost(irie_seed, original_network, mc, func=func)



