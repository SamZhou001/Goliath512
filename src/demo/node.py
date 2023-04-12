import argparse
import logging
import asyncio

from david.network import Server
from david.utils import digest

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('david')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

# log2 = logging.getLogger('rpcudp')
# log2.addHandler(handler)
# log2.setLevel(logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-p", "--port", help="port number of existing node", type=int, default=None)

    return parser.parse_args()


def connect_to_bootstrap_node(args):
    server = Server(node_id = digest(args.port), ksize=5)
    loop = asyncio.new_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(int(args.port)))
    IP = '0.0.0.0'
    bootstrap_node = (IP, 9000)
    loop.run_until_complete(server.bootstrap([bootstrap_node]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def create_bootstrap_node():
    server = Server(node_id = digest('9000'), ksize=5)
    loop = asyncio.new_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(9000))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def main():
    args = parse_arguments()

    if args.port:
        connect_to_bootstrap_node(args)
    else:
        create_bootstrap_node()


if __name__ == "__main__":
    main()