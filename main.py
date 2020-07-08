import numpy as np
import multiIC as IC
import multiRIS as RIS
import multiTDC as TDC
import multiCELF as CELF
import multiDegree as MAXDEG
import imbase

if __name__ == "__main__":
    # DBLP, NetHEPT, NetPHY

    Dataset = ['Random'] #, 'NetHEPT']
    k = 30
    p = 0.1
    mc = 10000
    num_cores = min(int(mp.cpu_count()), 24)

    print("%-9s  %-9s  %9s  %12s %9s" %('Dataset', 'Method', 'CostTime(s)', 'SimSpread', 'SimTime(s)'))
    print("%-9s  %-9s  %9s  %12s %9s" %('-------', '------', '-----------', '---------', '----------'))
    for dataset in Dataset:
        
        G = imbase.LoadDataset(dataset)

        tdc_output = TDC.main(G, k, dataset, p, num_cores=num_cores)
        spread, ictime = IC.main(G, dataset, tdc_output[0], p, mc)
        print("%-9s  %-9s  %9s  %12s %9s" %(dataset, 'TDC', tdc_output[1][-1], spread, ictime))

        ris_output = RIS.main(G, k, dataset, p, mc=50000, num_cores=num_cores)
        spread, ictime = IC.main(G, dataset, ris_output[0], p, mc)
        print("%-9s  %-9s  %9s  %12s %9s" %(dataset, 'RIS', ris_output[1][-1], spread, ictime))

        degree_output = MAXDEG.main(G, k, dataset, p, num_cores=num_cores)
        spread, ictime = IC.main(G, dataset, degree_output[0], p, mc)
        print("%-9s  %-9s  %9s  %12s %9s" %(dataset, 'maxDeg', degree_output[1][-1], spread, ictime))        

        # celf_output = CELF.main(G, k, dataset, p, mc=1000, num_cores=num_cores)
        # print("\n    CELF   Seed set: %s, Cost Time: %s(s)" %(celf_output[0], celf_output[1][-1]))
        # spread, ictime = IC.main(G, dataset, celf_output[0], p, mc)
        # print("    CELF   Spread:  %s, Simulation time: %s(s)" %(spread, ictime))