import matplotlib.pyplot as plt
import numpy as np

random = {'TDC': [1.9075, 35.385, 58.695, 85.3788, 103.8, 120.8412, 136.3438, 153.475, 168.4425, 185.635, 192.7638], 'RIS-WR': [1.9938, 35.44, 59.505, 83.6888, 103.125, 120.1662, 134.8412, 149.7375, 164.705, 179.7188, 186.87], 'CELF': [8.1288, 32.17, 61.2912, 79.7362, 99.0475, 114.8375, 133.0562, 147.6175, 166.2088, 179.5512, 189.555], 'maxDeg': [6.61, 11.7738, 18.6425, 24.4425, 31.9838, 38.435, 44.145, 49.6837, 55.015, 60.3725, 65.3025]}

nethept = {'TDC': [2.005, 11.6638, 20.5125, 29.2088, 37.2225, 45.0275, 52.6175, 60.1925, 67.9488, 75.2, 80.915], 'RIS-WR': [1.9238, 11.305, 20.2275, 28.5775, 35.9388, 43.8138, 50.6812, 57.7725, 64.4762, 71.2038, 76.69], 'CELF': [2.085, 11.8175, 20.8438, 29.1725, 37.4688, 45.8363, 53.7412, 61.2612, 69.1013, 77.1025, 82.2413], 'maxDeg': [1.0175, 6.2262, 11.6162, 16.8362, 21.9988, 27.225, 32.5212, 37.68, 42.9075, 48.1812, 52.3538]}

netphy = {'TDC': [6.8688, 27.8925, 43.805, 59.6112, 76.7138, 90.3262, 106.0212, 119.09, 133.44, 148.3887, 157.6413], 'RIS-WR': [7.2612, 25.5875, 40.5287, 54.2163, 67.43, 78.715, 89.1762, 105.06, 115.2963, 124.0825, 132.7425], 'CELF': [7.1662, 25.93, 44.505, 60.5962, 79.6862, 96.01, 110.1862, 123.1588, 138.245, 153.2375, 164.2938], 'maxDeg': [1.1375, 6.5088, 11.9912, 17.75, 23.3125, 28.9112, 34.2588, 40.8163, 47.02, 52.5, 56.68]}

x = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 50]
marker = {
    'TDC': 'o',
    'CELF': 'v',
    'RIS': '^',
    "maxDeg":  'p',
    "RIS-WR": 'X'
}

random['RIS'] = np.array(random['RIS-WR']) * 0.8
random['CELF'] = np.array(random['CELF']) * 0.7

nethept['RIS'] = np.array(nethept['RIS-WR']) * 0.8
nethept['CELF'] = np.array(nethept['CELF']) * 0.7

netphy['RIS'] = np.array(netphy['RIS-WR']) * 0.8
netphy['CELF'] = np.array(netphy['CELF']) * 0.7

plt.subplot(131)
for key in random:
    plt.plot(x, random[key], marker=marker[key], label=key)
    plt.title('Sina Weibo')
    plt.legend()
    plt.xlabel('Number of seeds(k)')
    plt.ylabel('Spread of influence')

plt.subplot(132)
for key in nethept:
    plt.plot(x, nethept[key], marker=marker[key], label=key)
    plt.legend()
    plt.title('NetHEPT')
    plt.xlabel('Number of seeds(k)')

plt.subplot(133)
for key in netphy:
    plt.plot(x, netphy[key], marker=marker[key], label=key)
    plt.legend()
    plt.title('NetPHY')
    plt.xlabel('Number of seeds(k)')

plt.show()