import numpy as np
import pandas as pd
import multiIC


if __name__ == "__main__":
    
    Random, NetHEPT, NetPHY = [], [], []
    allRecord = {
        'Random': {},
        'NetHEPT': {},
        'NetPHY': {}
    }
    with open('./Experiment.txt', 'r') as file:
        for temp in file.readlines():
            line = temp.split()
            key: list = line[0].split('-')
            dataset: dict = allRecord[key[0]]
            if key[1] not in dataset:
                dataset[key[1]] = [[int(line[1]), float(line[2])]]
            else:
                dataset[key[1]].append([int(line[1]), float(line[2])])

    for dKey in allRecord:
        print("Test Dataset %s:" %dKey)
        dataset = allRecord[dKey]
        for mKey in dataset:
            print("    Method %-4s has spread: " %mKey, end='')
            data = np.array(dataset[mKey], dtype=int)
            Seed = data[:, 0].tolist()
            print(multiIC.main(dKey, Seed, mc=20000))
        print("")
        


