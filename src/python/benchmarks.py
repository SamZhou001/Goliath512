import time
from network import Network
import constants
import asyncio


def bench_time(func):
    """
      decorator to calculate the total time of a func
    """

    def time_wrapper(*args, **keyArgs):
        print("WRAPPER WENT OFF")
        t1 = time.perf_counter()
        r = func(*args, **keyArgs)
        t2 = time.perf_counter()
        print("Test=%s, Time=%s" % (func.__name__, t2 - t1))
        return r

    return time_wrapper


@bench_time
async def test(network):
    cid = network.upload(100, "hi", 40)
    time.sleep(1)
    network.download(101, cid)
    time.sleep(1)
    network.kill_node(100)
    network.kill_node(101)
    network.kill_node(102)
    time.sleep(2)
    network.revive_node(100)
    network.revive_node(101)

if __name__ == "__main__":
    network = Network(constants.BOOTSTRAP_PORT)
    for config in constants.NODE_CONFIG:
        time.sleep(constants.SIM_INTERVAL)
        network.add_node(config)
    time.sleep(constants.SIM_INTERVAL)
    asyncio.run(test(network))
