import logging
import asyncio
import sys

from david.network import Server
from david.utils import digest

if len(sys.argv) != 3:
    print("Usage: python david_revive.py <node> <node port>")
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
    server = Server()
    await server.listen(0)
    addr = (sys.argv[1], int(sys.argv[2]))
    result = await server.revive(addr)
    print(result)
    server.stop()

asyncio.run(run())