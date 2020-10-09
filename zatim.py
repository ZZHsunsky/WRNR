'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-09-18 15:19:06
LastEditors: zehao zhao
LastEditTime: 2020-09-18 15:43:42
'''

from zutils import *
from collections import Counter
omega = 0.1

@fn_timer
def tim_node_selection(k: int, g: ZGraph, theta: int) -> List[int]:
    rr_sets = [g.get_a_rr_set() for i in range(theta)]
    S = []
    for i in range(k):
        flat_list = [item for sublist in rr_sets for item in sublist]
        seed = Counter(flat_list).most_common()[0][0]
        S.append(seed)

        # Remove RRSs containing last chosen seed
        rr_sets= [rrs for rrs in rr_sets if seed not in rrs]
    return S

def kpt_estimation(k: int, g: ZGraph):
    for i in range(1, math.log2(g.max_v)):
        c = 6 * omega * math.log(g.max_v) + 6 * math.log(math.log2(g.max_v))
        c = c * 2 ** i
        s = 0
