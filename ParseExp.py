import pandas as pd
import multiIC
import imbase
from cycler import cycler
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

mpl.rcParams['axes.prop_cycle'] = cycler(color=['#386BB0', '#F08961', '#E3191C', '#1C9E78'])

def drawSpreadPic(spread, x):
    marker = {
        'TDC': 'o',
        'CELF': 'v',
        'RIS': '^',
        "maxDeg":  'p'
    }
    pdf = PdfPages('spread.pdf')

    for key in spread:
        plt.plot(x, spread[key], marker=marker[key], label=key)
    
    plt.legend()
    plt.xlabel('Number of seeds(k)')
    plt.ylabel('Spread of influence')
    pdf.savefig()
    plt.close()
    pdf.close()

def drawTimePic(spread, x):
    marker = {
        'TDC': 'o',
        'CELF': 'v',
        'RIS': '^',
        "maxDeg":  'p'
    }
    pdf = PdfPages('runtime.pdf')
    y = [0, 1, 2, 3, 4]
    ytick = [ 10 ** i for i in y] 
    for key in spread:
        plt.plot(x, np.log10(spread[key]), marker=marker[key], label=key)
    
    plt.xlabel('Number of seeds(k)')
    plt.ylabel('Running time(s)')
    plt.yticks(y, ytick)
    plt.legend()
    pdf.savefig()
    plt.close()
    pdf.close()

if __name__ == "__main__":
    spread = {'TDC': [12.2927, 42.3326, 69.9747, 91.1313, 102.4035, 121.0995, 146.1053, 162.8012, 175.1666, 191.24, 197.4188], 'RIS': [12.3101, 44.8719, 69.3567, 91.5833, 108.8185, 127.3265, 144.2867, 159.0446, 170.9699, 188.9458, 196.9293], 'CELF': [12.2893, 41.2583, 67.1298, 81.895, 102.4449, 111.8791, 125.6106, 145.7103, 165.3212, 177.659, 181.6094], 'maxDeg': [6.8319, 24.9073, 40.9326, 49.165, 58.1633, 74.1376, 90.6737, 106.7565, 124.5186, 143.9497, 154.7243]}
    runtime = {'TDC': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 'RIS': [33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34], 'CELF': [2505, 2707, 3075, 3446, 3918, 4290, 4963, 5939, 7011, 8594, 10045], 'maxDeg': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]}
    x = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 30]
    drawSpreadPic(spread, x)
    drawTimePic(runtime, x)
    # Random, NetHEPT, NetPHY = [], [], []
    # allRecord = {
    #     'Random': {},
    #     'NetHEPT': {},
    #     'NetPHY': {}
    # }
    # with open('./Experiment.txt', 'r') as file:
    #     for temp in file.readlines():
    #         line = temp.split()
    #         key: list = line[0].split('-')
    #         dataset: dict = allRecord[key[0]]
    #         if key[1] not in dataset:
    #             dataset[key[1]] = [[int(line[1]), float(line[2])]]
    #         else:
    #             dataset[key[1]].append([int(line[1]), float(line[2])])

    # for dKey in allRecord:
    #     print("Test Dataset %s:" %dKey)
    #     dataset = allRecord[dKey]
    #     G = imbase.LoadDataset(dKey)
    #     ySpread = {}
    #     yRunTime = {}
    #     x = []
    #     for mKey in dataset:
    #         ySpread[mKey], yRunTime[mKey], x = [], [], []

    #         data = np.array(dataset[mKey], dtype=int)
    #         Seed = data[:, 0].tolist()
    #         Time = data[:, 1].tolist()
    #         for _ in range(10):
    #             idx = _ * (len(Seed) // 10)
    #             # ySpread[mKey].append(multiIC.main(G, dKey, Seed[:idx + 1])[0])
    #             yRunTime[mKey].append(Time[idx])
    #             x.append(idx + 1)
            
    #         # ySpread[mKey].append(multiIC.main(G, dKey, Seed)[0])
    #         yRunTime[mKey].append(Time[-1])
    #         x.append(len(Seed))
    #     print("")
    #     print(yRunTime)
    #     print(x)
        


