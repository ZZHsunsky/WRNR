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


if __name__ == "__main__":
    # Random network NetHEPTFix NetPHYFix
    network_type = 'network'
    k = 5
    mc = 10000

    # 加载原生图
    original_network = ZGraph()
    original_network.add_edge(1,2, 0.1)
    original_network.add_edge(2,1, 0.1)
    original_network.add_edge(1,3, 0.1)
    original_network.add_edge(3,1, 0.1)
    original_network.add_edge(2,3, 0.1)
    original_network.add_edge(3,2, 0.1)
    original_network.add_edge(1,4, 0.1)
    original_network.add_edge(4,1, 0.1)
    original_network.add_edge(2,4, 0.1)
    original_network.add_edge(4,2, 0.1)
    original_network.add_edge(3,4, 0.1)
    original_network.add_edge(4,3, 0.1)
    zmd_node_select(original_network)