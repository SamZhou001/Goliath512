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

log2 = logging.getLogger('rpcudp')
log2.addHandler(handler)
#log2.setLevel(logging.DEBUG)



def parse_arguments():
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-i", "--ip", help="IP address of existing node", type=str, default=None)
    parser.add_argument("-p", "--port", help="port number of existing node", type=int, default=None)

    return parser.parse_args()


def connect_to_bootstrap_node(args):
    server = Server(node_id = digest('9000'))
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(9000))
    bootstrap_node = (args.ip, int(args.port))
    loop.run_until_complete(server.bootstrap([bootstrap_node]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def create_bootstrap_node():
    server = Server(node_id = digest('8000'))
    loop = asyncio.new_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(8000))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def main():
    args = parse_arguments()

    if args.ip and args.port:
        connect_to_bootstrap_node(args)
    else:
        create_bootstrap_node()


if __name__ == "__main__":
    main()