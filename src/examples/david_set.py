import logging
import asyncio
import sys

from david.network import Server
from david.utils import digest


if len(sys.argv) != 3:
    print("Usage: python set.py <key> <value>")
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
    server = Server(node_id=digest('9010'), ksize=5, temporary=True)
    await server.listen(8470)
    bootstrap_node = ('0.0.0.0', 9000)
    print(await server.bootstrap([bootstrap_node]))
    await server.set(sys.argv[1], sys.argv[2])
    server.stop()

asyncio.run(run())