import time
from network import Network
import constants
import random
import os
import sys
import asyncio
import json

def sleep():
    time.sleep(constants.SIM_INTERVAL)

class Benchmark:
    
    def __init__(self):
        self.upload_times = {}
        self.download_times = {}
        self.download_prob = {}
        self.k = None
        self.n_nodes = None
        self.kill_chance = None

    async def test1(self, network, peer_ids):
        id1 = random.choice(peer_ids)
        t1 = time.perf_counter()
        cid = network.upload(id1, "hi", 40)
        t2 = time.perf_counter()
        self.upload_times[self.k][self.n_nodes][self.kill_chance] = t2 - t1
        sleep()
        peer_ids_copy = list(peer_ids)
        peer_ids_copy.remove(id1)
        download_t = []
        killed_nodes = []
        successes = 0
        for _ in range(min(len(peer_ids)//2, 10)):
            id2 = random.choice(peer_ids_copy)
            peer_ids_copy.remove(id2)
            for peer_id in peer_ids:
                if random.random() < self.kill_chance and peer_id != id2: # kill node
                    if peer_id not in killed_nodes:
                        await network.kill_node(peer_id)
                        killed_nodes.append(peer_id)
                else:
                    if peer_id in killed_nodes:
                        await network.revive_node(peer_id)
                        killed_nodes.remove(peer_id)
            sleep()
            t1 = time.perf_counter()
            network.download(id2, cid)
            fname = str(id1) + "_hi.txt"
            for i in range(25):
                if fname in list(os.listdir(os.path.join("./storage/", str(id2), "uploaded"))):
                    t2 = time.perf_counter()
                    download_t.append(t2-t1)
                    successes += 1
                    break
                time.sleep(0.2)
        for peer_id in killed_nodes:
            await network.revive_node(peer_id)
            killed_nodes.remove(peer_id)
        if len(download_t) > 0:
            self.download_times[self.k][self.n_nodes][self.kill_chance] = sum(download_t)/len(download_t)
        else:
            self.download_times[self.k][self.n_nodes][self.kill_chance] = 0
        self.download_prob[self.k][self.n_nodes][self.kill_chance] = successes/min(len(peer_ids)//2, 10)

    async def test2(self, network, peer_ids): # multiple uploads
        upload_t = []
        testing_pairs = []
        for i in range(10):
            id1 = random.choice(peer_ids)
            t1 = time.perf_counter()
            cid = network.upload(id1, str(i), 40)
            t2 = time.perf_counter()
            testing_pairs += [(peer_id, cid, str(i), id1) for peer_id in peer_ids if peer_id != id1]
            upload_t.append(t2-t1)
        self.upload_times[self.k][self.n_nodes][self.kill_chance] = sum(upload_t)/len(upload_t)
        sleep()
        testing_pairs_copy = list(testing_pairs)
        download_t = []
        killed_nodes = []
        successes = 0
        for _ in range(10):
            id2, cid, i, id1 = random.choice(testing_pairs_copy)
            testing_pairs_copy.remove((id2, cid, i, id1))
            for peer_id in peer_ids:
                if random.random() < self.kill_chance and peer_id != id2: # kill node
                    if peer_id not in killed_nodes:
                        await network.kill_node(peer_id)
                        killed_nodes.append(peer_id)
                else:
                    if peer_id in killed_nodes:
                        await network.revive_node(peer_id)
                        killed_nodes.remove(peer_id)
            sleep()
            t1 = time.perf_counter()
            network.download(id2, cid)
            fname = str(id1) + "_hi.txt"
            for i in range(25):
                if fname in list(os.listdir(os.path.join("./storage/", str(id2), "uploaded"))):
                    t2 = time.perf_counter()
                    download_t.append(t2-t1)
                    successes += 1
                    break
                time.sleep(0.2)
        for peer_id in killed_nodes:
            await network.revive_node(peer_id)
            killed_nodes.remove(peer_id)
        if len(download_t) > 0:
            self.download_times[self.k][self.n_nodes][self.kill_chance] = sum(download_t)/len(download_t)
        else:
            self.download_times[self.k][self.n_nodes][self.kill_chance] = 0
        self.download_prob[self.k][self.n_nodes][self.kill_chance] = successes/10

    async def full_test(self, testNum, parameters):
        assert testNum in [1, 2]
        counter = 0
        total_params = len(parameters['k']) * len(parameters['nodes']) * len(parameters['kill_chance'])
        for k in parameters['k']:
            self.k = k
            self.upload_times[k] = {}
            self.download_times[k] = {}
            self.download_prob[k] = {}
            for n_nodes in parameters['nodes']:
                self.n_nodes = n_nodes
                self.upload_times[k][n_nodes] = {}
                self.download_times[k][n_nodes] = {}
                self.download_prob[k][n_nodes] = {}
                for kill_chance in parameters['kill_chance']:
                    print(f"Progress: {counter}/{total_params}", end="\r")
                    network = Network(constants.BOOTSTRAP_PORT, k, True)
                    config = constants.node_config(n_nodes)
                    peer_ids = [c['peer_id'] for c in config]
                    for c in config:
                        sleep()
                        network.add_node(c)
                    self.kill_chance = kill_chance
                    self.upload_times[k][n_nodes][kill_chance] = {}
                    self.download_times[k][n_nodes][kill_chance] = {}
                    self.download_prob[k][n_nodes][kill_chance] = {}
                    sleep()
                    if testNum == 1:
                        await self.test1(network, peer_ids)
                    else:
                        await self.test2(network, peer_ids)
                    counter += 1
                    network.kill()
        return self.upload_times, self.download_times, self.download_prob

if __name__ == "__main__":
    benchmark = Benchmark()

    upload_times_1, download_times_1, download_prob_1 = asyncio.run(benchmark.full_test(1, constants.PARAMETERS_1))
    data_k_1 = {
        "upload_time": upload_times_1, 
        "download_time": download_times_1, 
        "download_prob": download_prob_1
    }
    with open('data_k_1.json', 'w') as f:
        json.dump(data_k_1, f)

    upload_times_1, download_times_1, download_prob_1 = asyncio.run(benchmark.full_test(1, constants.PARAMETERS_2))
    data_n_1 = {
        "upload_time": upload_times_1, 
        "download_time": download_times_1, 
        "download_prob": download_prob_1
    }
    with open('data_n_1.json', 'w') as f:
        json.dump(data_n_1, f)
    '''
    upload_times_2, download_times_2, download_prob_2 = asyncio.run(benchmark.full_test(2, constants.PARAMETERS_1))
    data_k_2 = {
        "upload_time": upload_times_2, 
        "download_time": download_times_2, 
        "download_prob": download_prob_2
    }
    with open('data_k_2.json', 'w') as f:
        json.dump(data_k_2, f)

    upload_times_2, download_times_2, download_prob_2 = asyncio.run(benchmark.full_test(2, constants.PARAMETERS_2))
    data_n_2 = {
        "upload_time": upload_times_2, 
        "download_time": download_times_2, 
        "download_prob": download_prob_2
    }
    with open('data_n_2.json', 'w') as f:
        json.dump(data_n_2, f)
    '''
