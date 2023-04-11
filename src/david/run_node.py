import logging
import asyncio
import os

from david.network import Server
from david.utils import digest

logging.basicConfig(
    filename='/home/app/david/log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

def create_port_to_node_id_mapping(num):
    BASE = 9000
    PORTS = [i for i in range(BASE, BASE+num)]
    map = {}
    for port in PORTS:
        map[port] = digest(str(port))
    
    return map

PORT_TO_NODE_ID_MAP = create_port_to_node_id_mapping(10)

def create_bootstrap_node(port):
    server = Server(PORT_TO_NODE_ID_MAP.get(port))
    loop = asyncio.new_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()

def connect_to_bootstrap_node(port):
    server = Server(PORT_TO_NODE_ID_MAP.get(port))
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(port))
    bootstrap_node = ('0.0.0.0', port)
    loop.run_until_complete(server.bootstrap([bootstrap_node]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()

def main():
    PORT = int(os.getenv('PORT'))
    if PORT == 9000:
        create_bootstrap_node(PORT)
    else:
        connect_to_bootstrap_node(PORT)

if __name__ == "__main__":
    main()