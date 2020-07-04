import matplotlib.pyplot as plt
from random import uniform, seed
import numpy as np
import pandas as pd
import time
from igraph import *
import random
from collections import Counter
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt

def IC(G,S,p=0.5,mc=1000):  
    """
    Input:  G:  Ex2 dataframe of directed edges. Columns: ['source','target']
            S:  Set of seed nodes
            p:  Disease propagation probability
            mc: Number of Monte-Carlo simulations
    Output: Average number of nodes influenced by the seed nodes
    """
    
    # Loop over the Monte-Carlo Simulations
    spread = []
    for _ in range(mc):
        
        # Simulate propagation process      
        new_active, A = S[:], S[:]
        deep = 1
        while new_active:
            
            # Get edges that flow out of each newly active node
            temp = G.loc[G['source'].isin(new_active)]

            # Extract the out-neighbors of those nodes
            targets = temp['target'].tolist()

            # Determine those neighbors that become infected
            success  = np.random.uniform(0,1,len(targets)) < p
            new_ones = np.extract(success, targets)

            # Create a list of nodes that weren't previously activated
            new_active = list(set(new_ones) - set(A))
                        
            # print(deep, len(new_active), len(targets))
            deep += 1
            # Add newly activated nodes to the set of activated nodes
            A += new_active
            
        spread.append(len(A))
        
    return(np.mean(spread))

def celf(G,k,p=0.5,mc=1000):   
    """
    Inputs: G:  Ex2 dataframe of directed edges. Columns: ['source','target']
            k:  Size of seed set
            p:  Disease propagation probability
            mc: Number of Monte-Carlo simulations
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
      
    # --------------------
    # Find the first node with greedy algorithm
    # --------------------
    
    # Compute marginal gain for each node
    candidates, start_time = np.unique(G['source']), time.time()
    marg_gain = [IC(G,[node],p=p,mc=mc) for node in candidates]

    # Create the sorted list of nodes and their marginal gain 
    Q = sorted(zip(candidates,marg_gain), key = lambda x: x[1],reverse=True)

    # Select the first node and remove from candidate list
    S, spread, Q = [Q[0][0]], Q[0][1], Q[1:]
    timelapse = [time.time() - start_time]
    
    # --------------------
    # Find the next k-1 nodes using the CELF list-sorting procedure
    # --------------------
    
    for _ in range(k-1):    

        check = False      
        while not check:
            
            # Recalculate spread of top node
            current = Q[0][0]
            
            # Evaluate the spread function and store the marginal gain in the list
            Q[0] = (current,IC(G,S+[current],p=p,mc=mc) - spread)

            # Re-sort the list
            Q = sorted(Q, key = lambda x: x[1], reverse=True)

            # Check if previous top node stayed on top after the sort
            check = Q[0][0] == current

        # Select the next node
        S.append(Q[0][0])
        spread = Q[0][1]
        timelapse.append(time.time() - start_time)
        
        # Remove the selected node from the list
        Q = Q[1:]
    
    return(sorted(S),timelapse)

def get_RRS(G: pd.DataFrame, p: float):
    """
    Inputs: G: Ex2 dataFrame of directed edges. Columns: ['source', 'target']
            p: Dosease propagation probability
    Return: A random reverse rachable set expressed as a list of nodes
    """
    # Step 1. Select random source node
    source = random.choice(np.unique(G['source']))
    # Step 2. Get an instance of g from G by sampling edges
    g: pd.DataFrame = G.copy().loc[np.random.uniform(0, 1, G.shape[0]) < p]
    # Step 3. Construct reverse set of the random source node
    new_nodes, RRS0 = [source], [source]

    while new_nodes:

        # Limit to edges that flow into the source node
        temp = g.loc[g['target'].isin(new_nodes)]

        # Extract the nodes flowing into the source node
        temp = temp['source'].tolist()

        # Add new set of in-neighbors to the RRS
        RRS = list(set(RRS0 + temp))

        # Find what new nodes were added
        new_nodes = list(set(RRS) - set(RRS0))

        # Reset loop variables
        RRS0 = RRS[:]
    
    return RRS

def ris(G: pd.DataFrame, k: int, p=0.5, mc=1000):
    """
    Inputs: G:  Ex2 dataframe of directed edges. Columns: ['source','target']
            k:  Size of seed set
            p:  Disease propagation probability
            mc: Number of RRSs to generate
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
    # Step 1. Generate the collection of random RRSs
    start_time = time.time()
    mc *= 10
    R = [get_RRS(G, p) for _ in range(mc)]

    # Step 2. Choose nodes that appear most ofen(maximum coverage greedy algorithm)
    SEED, timelapse = [], []
    for _ in range(k):
        # Find node that occurs most often in R and add to seed set
        flat_list = [item for sublist in R for item in sublist]
        seed = Counter(flat_list).most_common()[0][0]
        SEED.append(seed)

        # Remove RRSs containing last chosen seed
        R = [rrs for rrs in R if seed not in rrs]

        # Record Time
        timelapse.append(time.time() - start_time)
    return(sorted(SEED),timelapse)

def tdc(G: pd.DataFrame, k:int, p = 0.5, mc=1000):
    # Compute marginal gain for each node
    candidates, start_time = np.unique(G['source']), time.time()
    n = candidates.shape[0]
    def DDI(idx: int, limit = 0.0001):
        deep, tdvalue = 1, 1.0
        new_children, A = [idx], [idx]
        while new_children:
            decay = p ** deep
            if decay< limit:
                break
            temp = G.loc[G['source'].isin(new_children)]
            targets = temp['target'].tolist()

            tdvalue += decay * len(targets)
            new_children = list(set(targets) - set(A))
            A += new_children
            deep += 1
        return tdvalue
    td_list = [DDI(idx) for idx in candidates]
    Q = sorted(zip(candidates,td_list), key = lambda x: x[1],reverse=True)
    
    SEED , timelapse = [], []
    for _ in range(k):
        SEED.append(Q[0][0])
        Q = Q[1:]
        timelapse.append(round(time.time() - start_time, 4))

    return(sorted(SEED),timelapse)

def searchTDC(G: pd.DataFrame, target: int, p = 0.5):
    candidates, start_time = np.unique(G['source']), time.time()
    def DDI(idx: int, limit = 0.0001):
        deep, tdvalue = 1, 1.0
        new_children, A = [idx], [idx]
        traverse = pd.DataFrame({'source': [], 'target': []}, dtype=int)
        while new_children:
            decay = p ** deep
            if decay< limit:
                break
            temp = G.loc[G['source'].isin(new_children)]
            traverse = pd.concat([traverse, temp])
            targets = temp['target'].tolist()
            tdvalue += decay * len(targets)
            new_children = list(set(targets) - set(A))
            # print(deep, len(new_children))
            A += new_children
            deep += 1
        return tdvalue, traverse
    return DDI(target)

def maxDegree(G: pd.DataFrame, k:int, p = 0.5):
    candidates, start_time = np.unique(G['source']), time.time()
    degree = [G.loc[G['source'].isin([_])]['target'].shape[0] for _ in candidates]
    Q = sorted(zip(candidates, degree), key=lambda x: x[1], reverse=True)
    SEED , timelapse = [], []
    for _ in range(k):
        SEED.append(Q[0][0])
        Q = Q[1:]
        timelapse.append(time.time() - start_time)

    return(sorted(SEED),timelapse)

def runExperiment(df: pd.DataFrame, k: int, p: float, mc: int, keys):
    func = {
        "TDC": tdc,
        "RIS": ris,
        "CELF": celf,
        "MaxD": maxDegree,
    }
    if type(keys) != type([]):
        keys = func.keys()
    
    for key in keys:
        output = func[key](df, k, p, mc)
        print("\n%s Seed set: %s, Cost Time: %s(s)" %(key, output[0], output[1][-1]))
        spread = IC(df, output[0], p, mc)
        print("%s Spread:  %s" %(key, spread))

def LoadDataset(name="NetHEPT", drop_dup=True):
    if name == 'Random':
        return RandomDataset()
    dataset = np.loadtxt('./Data/' + name + '.txt', skiprows=1, dtype=int)
    df = pd.DataFrame(dataset, columns=['source', 'target'])
    if drop_dup:
        df.drop_duplicates(inplace=True)
    return df

def RandomDataset():
    G = Graph.Barabasi(n=4096, m=8,directed=True)
    # Transform into dataframe of edges
    source_nodes = [edge.source for edge in G.es]
    target_nodes = [edge.target for edge in G.es]
    df = pd.DataFrame({'source': source_nodes,'target': target_nodes})
    return df

def DrawTreeNetwork(traverse: pd.DataFrame):
    G =nx.from_pandas_edgelist(traverse, 'source', 'target')
    # Plot it
    nx.draw(G, with_labels=True, node_size=1500, font_size=12, font_color="yellow", font_weight="bold", pos=graphviz_layout(G, prog='dot'))
    plt.show()


if __name__ == "__main__":
    G = LoadDataset('Random')
    # SEED, timelapse = ris(G, 10, 0.1, 50000)
    start_time = time.time()
    SEED = [3107, 3567, 3454, 3554, 3642, 2701, 3530, 2785, 2822, 2827]
    spread = IC(G, SEED, p=0.1, mc=10000)
    # print(sorted(SEED))
    # print(timelapse)
    print(spread, time.time() - start_time)







