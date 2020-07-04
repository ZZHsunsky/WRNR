import numpy as np
import multiIC as IC
import multiRIS as RIS
import multiTDC as TDC
import multiCELF as CELF
import imbase

if __name__ == "__main__":
    # DBLP, NetHEPT, NetPHY

    Dataset = ['Random'] #, 'NetHEPT']
    k = 10
    p = 0.1
    mc = 10000
    for dataset in Dataset:
        
        print("Test Dataset %s, with p = %s and mc = %s:" %(dataset, p, mc))
        G = imbase.LoadDataset(dataset)

        tdc_output = TDC.main(G, k, dataset, p)
        print("\n    TDC    Seed set: %s, Cost Time: %s(s)" %(tdc_output[0], tdc_output[1][-1]))
        spread, ictime = IC.main(G, dataset, tdc_output[0], p, mc)
        print("    TDC    Spread:  %s, Simulation time: %s(s)" %(spread, ictime))

        ris_output = RIS.main(G, k, dataset, p, mc=50000)
        print("\n    RIS    Seed set: %s, Cost Time: %s(s)" %(ris_output[0], ris_output[1][-1]))
        spread, ictime = IC.main(G, dataset, ris_output[0], p, mc)
        print("    RIS    Spread:  %s, Simulation time: %s(s)" %(spread, ictime))

        degree_output = imbase.maxDegree(G, k, p)
        print("\n    maxDeg Seed set: %s, Cost Time: %s(s)" %(degree_output[0], degree_output[1][-1]))
        spread, ictime = IC.main(G, dataset, degree_output[0], p, mc)
        print("    maxDeg Spread:  %s, Simulation time: %s(s)" %(spread, ictime))

        celf_output = CELF.main(G, k, dataset, p, mc=1000)
        print("\n    CELF   Seed set: %s, Cost Time: %s(s)" %(celf_output[0], celf_output[1][-1]))
        spread, ictime = IC.main(G, dataset, celf_output[0], p, mc)
        print("    CELF   Spread:  %s, Simulation time: %s(s)" %(spread, ictime))