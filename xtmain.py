'''
Descripttion: 
version: 
Author: zehao zhao
Date: 2020-10-09 17:08:47
LastEditors: zehao zhao
LastEditTime: 2020-10-09 17:30:21
'''
import requests
import json
import csv

#xt_BeamRiderNoFrameskip-v4_DQN_cpu20

def parse(env, alg, cpu, target="_time"):

    key = "xt_{}_{}_{}".format(env, alg, cpu)
    Exp = data[key]
    features = list(Exp[-1].keys())

    for item in ["_step", "_time", "episode_reward_mean", "mean_predictor_wait_ms", "'mean_predictor_infer_ms", "sys_perf_event_open()", "|"]:
        if item in features:
            features.remove(item)

    features.append(target)

    csvFile = open('./xt_data/{}-{}.csv'.format(alg, target), 'w', newline='')
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(features)

    for i in range(len(Exp)):
        temp = []
        line = Exp[i]
        for item in features:
            if item in line:
                temp.append(line[item])
            else:
                temp.append('nan')
                print(item)
        csvWriter.writerow(temp)

res = requests.get("http://192.168.1.128:3000/xtGetAll")
data: dict = json.loads(res.text)

parse("BeamRiderNoFrameskip-v4", "DQN", "cpu20")
parse("BeamRiderNoFrameskip-v4", "IMPALA", "cpu20")
parse("BeamRiderNoFrameskip-v4", "PPO", "cpu20")

parse("BeamRiderNoFrameskip-v4", "DQN", "cpu20", "episode_reward_mean")
parse("BeamRiderNoFrameskip-v4", "IMPALA", "cpu20", "episode_reward_mean")
parse("BeamRiderNoFrameskip-v4", "PPO", "cpu20", "episode_reward_mean")
