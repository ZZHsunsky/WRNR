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


    k = 100
    mc = 1000

    network_type = "EpinionsFix"
    

    # 加载原生图

    g = ZGraph()
    sp_a = load_network(g, network_type)

    rg = ZGraph()
    load_network(rg, network_type, reverse=True)

    func = sigmod_func
    
    ris_seed, runtime = tim_node_selection(k, rg, mc * 100)
    calc_sigma_in_networks_with_cost(ris_seed, g, func=func)

    max_degree_seed, runtime = max_degree_in_origin_network(k, g)
    calc_sigma_in_networks_with_cost(max_degree_seed, g, func=func)

    # calc_sigma_in_networks_with_cost(ris_seed, g, mc, func=func)

    # zmd_seed, runtime = IRIE(k, g, sp_a, func)

    # func = slow_fast_increase
    # irie_seed, runtime = IRIE(k,g, sp_a, func)
    # calc_sigma_in_networks_with_cost(irie_seed, g, mc, func=func)



