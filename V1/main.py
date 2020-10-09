import numpy as np
import multiIC as IC
import multiRIS as RIS
import multiTDC as TDC
import multiCELF as CELF
import multiDegree as MAXDEG
import imbase
import multiprocessing  as mp

if __name__ == "__main__":
    # DBLP, NetHEPT, NetPHY

    Dataset = ['Random', 'NetHEPT' ,'NetPHY'] #, 'NetHEPT']
    k = 10
    p = 0.1
    mc = 10000
    num_cores = 1

    print("%-9s  %-9s  %12s  %12s    %9s" %('Dataset', 'Method', 'CostTime(s)', 'SimSpread', 'SimTime(s)'))
    print("%-9s  %-9s  %12s  %12s    %9s" %('-------', '------', '-----------', '---------', '----------'))
    for dataset in Dataset:

        G = imbase.LoadDataset(dataset)

        # tdc_output = TDC.main(G, k, dataset, p, num_cores=num_cores)
        # spread, ictime = IC.main(G, dataset, tdc_output[0], p, mc, num_cores=num_cores)
        tdc_output = imbase.tdc(G, k, p)
        spread, ictime = imbase.IC(G, tdc_output[0], p, mc), "None"
        print("%-9s  %-9s  %12s  %12f    %9s" %(dataset, 'TDC', tdc_output[1][-1], spread, ictime))

        # ris_output = RIS.main(G, k, dataset, p, mc=50000, num_cores=num_cores)
        # spread, ictime = IC.main(G, dataset, ris_output[0], p, mc, num_cores=num_cores)
        ris_output = imbase.ris(G, k, p, mc=10000)
        spread, ictime = imbase.IC(G, ris_output[0], p, mc), "None"
        print("%-9s  %-9s  %12s  %12f    %9s" %(dataset, 'RIS', ris_output[1][-1], spread, ictime))

        # degree_output = MAXDEG.main(G, k, dataset, p, num_cores=num_cores)
        # spread, ictime = IC.main(G, dataset, degree_output[0], p, mc, num_cores=num_cores)
        degree_output = imbase.maxDegree(G, k, p)
        spread, ictime = imbase.IC(G, degree_output[0], p, mc), "None"
        print("%-9s  %-9s  %12s  %12f    %9s" %(dataset, 'maxDeg', degree_output[1][-1], spread, ictime))

        # celf_output = CELF.main(G, k, dataset, p, mc=100, num_cores=num_cores)
        # spread, ictime = None, None #IC.main(G, dataset, degree_output[0], p, mc, num_cores=num_cores)
        # print("%-9s  %-9s  %9s  %12s    %9s" %(dataset, 'CELF', celf_output[1][-1], spread, ictime))