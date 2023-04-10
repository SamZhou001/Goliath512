import time
from network import Network
import constants
import random
import os

def sleep():
    time.sleep(constants.SIM_INTERVAL)

class Benchmark:

    def __init__(self):
        self.upload_times = {}
        self.download_times = {}
        self.download_prob = {}
        self.k = None
        self.n_nodes = None
        self.regional = None
        self.kill_chance = None

    def test1(self, network, peer_ids):
        id1 = random.choice(peer_ids)
        t1 = time.perf_counter()
        cid = network.upload(id1, "hi", 40)
        t2 = time.perf_counter()
        self.upload_times[self.k][self.n_nodes][self.regional][self.kill_chance] = t2 - t1
        sleep()
        peer_ids_copy = list(peer_ids)
        peer_ids_copy.remove(id1)
        download_t = []
        killed_nodes = []
        successes = 0
        for _ in range(10):
            id2 = random.choice(peer_ids_copy)
            for peer_id in peer_ids:
                if random.random() < self.kill_chance and peer_id != id2: # kill node
                    if peer_id not in killed_nodes:
                        network.kill_node(peer_id)
                        killed_nodes.append(peer_id)
                else:
                    if peer_id in killed_nodes:
                        network.revive_node(peer_id)
                        killed_nodes.remove(peer_id)
            t1 = time.perf_counter()
            network.download(id2, cid)
            t2 = time.perf_counter()
            #time.sleep(constants.DOWNLOAD_TIMER)
            fname = str(id1) + "_hi.txt"
            if fname in list(os.listdir(os.path.join("./storage/"), id2, "uploaded")):
                download_t.append(t2-t1)
                successes += 1
        self.download_times[self.k][self.n_nodes][self.regional][self.kill_chance] = sum(download_t)/len(download_t)
        self.download_prob[self.k][self.n_nodes][self.regional][self.kill_chance] = successes/10
        sleep()

    def test2(self, network, peer_ids): # multiple uploads
        pass

    def full_test(self, testNum):
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
                for regional in constants.PARAMETERS['regional']:
                    self.regional = regional
                    self.upload_times[k][n_nodes][regional] = {}
                    self.download_times[k][n_nodes][regional] = {}
                    self.download_prob[k][n_nodes][regional] = {}
                    for kill_chance in constants.PARAMETERS['kill_chance']:
                        self.kill_chance = kill_chance
                        self.upload_times[k][n_nodes][regional][kill_chance] = {}
                        self.download_times[k][n_nodes][regional][kill_chance] = {}
                        self.download_prob[k][n_nodes][regional][kill_chance] = {}
                        network = Network(constants.BOOTSTRAP_PORT)
                        config = constants.node_config(n_nodes, regional)
                        peer_ids = [c['peer_id'] for c in config]
                        for config in constants.NODE_CONFIG:
                            sleep()
                            network.add_node(config)
                        sleep()
                        if testNum == 1:
                            self.test1(network, peer_ids)
                        else:
                            self.test2(network, peer_ids)
        return self.upload_times, self.download_times, self.download_prob

if __name__ == "__main__":
    benchmark = Benchmark()
    upload_times_1, download_times_1, download_prob_1 = benchmark.full_test(1)
    upload_times_2, download_times_2, download_prob_2 = benchmark.full_test(2)



    
