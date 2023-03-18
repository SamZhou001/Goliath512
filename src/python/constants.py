PING_TIMER = 0.5 # Time between each ping
BOOTSTRAP_PORT = 18861
SIM_INTERVAL = 1 # Amount of time between each step in network main function
NODE_CONFIG = [
    {
        "peer_id": 100,
        "port": 8000,
        "connect_prob": 0.5
    },
    {
        "peer_id": 101,
        "port": 8001,
        "connect_prob": 0.7
    },
    {
        "peer_id": 102,
        "port": 8002,
        "connect_prob": 1
    },
]