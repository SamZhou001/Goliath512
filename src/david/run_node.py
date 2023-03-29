import argparse
import logging
import asyncio

from david.network import Server

logging.basicConfig(
    filename='/home/app/david/log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

server = Server()

def parse_arguments():
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-i", "--ip", help="IP address of existing node", type=str, default=None)
    parser.add_argument("-p", "--port", help="port number of existing node", type=int, default=None)

    return parser.parse_args()


def connect_to_bootstrap_node(args):
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    loop.run_until_complete(server.listen(8469))
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