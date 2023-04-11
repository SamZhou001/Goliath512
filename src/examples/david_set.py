import logging
import asyncio
import sys

from david.network import Server
from david.utils import digest


if len(sys.argv) != 5:
    print("Usage: python set.py <bootstrap node> <bootstrap port> <key> <value>")
    sys.exit(1)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('david')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

log2 = logging.getLogger('rpcudp')
log2.addHandler(handler)
log2.setLevel(logging.DEBUG)

async def run():
    server = Server(node_id=digest('9010'), ksize=3)
    await server.listen(8470)
    bootstrap_node = (sys.argv[1], int(sys.argv[2]))
    await server.bootstrap([bootstrap_node])
    await server.set(sys.argv[3], sys.argv[4])
    server.stop()

asyncio.run(run())