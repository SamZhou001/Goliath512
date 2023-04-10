import time
from network import Network
import constants
import random
import os
import asyncio

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
            t1 = time.perf_counter()
            network.download(id2, cid)
            #time.sleep(constants.DOWNLOAD_TIMER)
            fname = str(id1) + "_hi.txt"
            for i in range(20):
                if fname in list(os.listdir(os.path.join("./storage/", str(id2), "uploaded"))):
                    t2 = time.perf_counter()
                    download_t.append(t2-t1)
                    successes += 1
                    break
                time.sleep(0.1)
        self.download_times[self.k][self.n_nodes][self.kill_chance] = sum(download_t)/len(download_t)
        self.download_prob[self.k][self.n_nodes][self.kill_chance] = successes/len(download_t)

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
            t1 = time.perf_counter()
            network.download(id2, cid)
            #time.sleep(constants.DOWNLOAD_TIMER)
            fname = str(id1) + "_hi.txt"
            for i in range(20):
                if fname in list(os.listdir(os.path.join("./storage/", str(id2), "uploaded"))):
                    t2 = time.perf_counter()
                    download_t.append(t2-t1)
                    successes += 1
                    break
                time.sleep(0.1)
        self.download_times[self.k][self.n_nodes][self.kill_chance] = sum(download_t)/len(download_t)
        self.download_prob[self.k][self.n_nodes][self.kill_chance] = successes/10

    async def full_test(self, testNum):
        assert testNum in [1, 2]
        for k in constants.PARAMETERS['k']:
            self.k = k
            self.upload_times[k] = {}
            self.download_times[k] = {}
            self.download_prob[k] = {}
            for n_nodes in constants.PARAMETERS['nodes']:
                self.n_nodes = n_nodes
                self.upload_times[k][n_nodes] = {}
                self.download_times[k][n_nodes] = {}
                self.download_prob[k][n_nodes] = {}
                network = Network(constants.BOOTSTRAP_PORT, k)
                config = constants.node_config(n_nodes)
                peer_ids = [c['peer_id'] for c in config]
                for c in config:
                    sleep()
                    network.add_node(c)
                for kill_chance in constants.PARAMETERS['kill_chance']:
                    self.kill_chance = kill_chance
                    self.upload_times[k][n_nodes][kill_chance] = {}
                    self.download_times[k][n_nodes][kill_chance] = {}
                    self.download_prob[k][n_nodes][kill_chance] = {}
                    sleep()
                    if testNum == 1:
                        await self.test1(network, peer_ids)
                    else:
                        await self.test2(network, peer_ids)
        return self.upload_times, self.download_times, self.download_prob

if __name__ == "__main__":
    benchmark = Benchmark()
    upload_times_1, download_times_1, download_prob_1 = asyncio.run(benchmark.full_test(1))
    print(upload_times_1, download_times_1, download_prob_1)
    #upload_times_2, download_times_2, download_prob_2 = asyncio.run(benchmark.full_test(2))



    
