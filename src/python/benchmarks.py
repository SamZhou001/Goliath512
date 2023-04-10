import time
from network import Network
import constants
import asyncio

async def test(network):
    t1 = time.perf_counter()
    cid = network.upload(100, "hi", 40)
    time.sleep(1)
    network.download(101, cid)
    time.sleep(1)
    await network.kill_node(100)
    await network.kill_node(101)
    await network.kill_node(102)
    time.sleep(2)
    await network.revive_node(100)
    await network.revive_node(101)
    t2 = time.perf_counter()
    print(t2 - t1)

if __name__ == "__main__":
    network = Network(constants.BOOTSTRAP_PORT)
    for config in constants.NODE_CONFIG:
        time.sleep(constants.SIM_INTERVAL)
        network.add_node(config)
    time.sleep(constants.SIM_INTERVAL)
    asyncio.run(test(network))
