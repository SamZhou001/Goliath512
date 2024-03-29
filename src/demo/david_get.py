import logging
import asyncio
import sys

from david.network import Server
from david.utils import digest


if len(sys.argv) != 2:
    print("Usage: python get.py <key>")
    sys.exit(1)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('david')
log.addHandler(handler)
log.setLevel(logging.INFO)

async def run():
    server = Server(node_id = digest('5000'), ksize=5, temporary=True)
    await server.listen(0)
    bootstrap_node = ('0.0.0.0', 9000)
    print(await server.bootstrap([bootstrap_node]))
    result = await server.get(sys.argv[1])
    print("Get result:", result)
    server.stop()

asyncio.run(run())
