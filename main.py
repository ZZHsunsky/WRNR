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
from zirie import IRIE

import logging

logging.basicConfig(level=logging.INFO)
sys.setrecursionlimit(2000000)

if __name__ == "__main__":
    # Random network NetHEPTFix NetPHYFix EpinionsFix
    network_type = 'EpinionsFix'
    k = 50
    mc = 1000


    # 加载原生图
    g = ZGraph()
    sp_a = load_network(g, network_type)

    rg = ZGraph()
    load_network(rg, network_type, reverse=True)
    
    func = slow_fast_increase

    # CELF
    # celf_seed, runtime = celf_in_origin_network(k, g, mc=1000)
    # record_experimnet_result(g, celf_seed, network_type, 'CELF++', runtime)

    # max degree
    # max_degree_seed, runtime = max_degree_in_origin_network(k, g)
    # record_experimnet_result(g, max_degree_seed, network_type, 'MaxDegree', runtime)

    # # ris 
    # ris_seed, runtime = tim_node_selection(k, rg, mc * 100)
    # record_experimnet_result(g, ris_seed, network_type, 'TIM', runtime)


    # # zmd
    # zmd_seed, runtime = zmd_node_select(k, g)
    # record_experimnet_result(g, zmd_seed, network_type, 'StaticGreedy', runtime)


    # IRIE
    irie_seed, runtime = IRIE(k, g, sp_a, func)
    record_experimnet_result(g, irie_seed, network_type, 'ICT', runtime)

    celf_seed, runtime = celf_in_origin_network(k, g, mc=1000)
    record_experimnet_result(g, celf_seed, network_type, 'CELF++', runtime)

    print("")
