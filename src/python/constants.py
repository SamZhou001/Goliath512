PING_TIMER = 0.5 # Time between each ping
BOOTSTRAP_PORT = 18861
SIM_INTERVAL = 1 # Amount of time between each step in network main function
HASH_DIGITS = 16 # Number of digits of each cid and dhtId
NUM_NODES = 3
BASE_LATENCY = 30 # ms
REGIONS = ["USA", "South Africa", "Central Europe", "Brazil", "China", "Australia"]
DISTANCES = [
    [0, 12800, 6700, 7800, 11500, 16200],
    [12800, 0, 9200, 6900, 6800, 11700],
    [6700, 9200, 0, 9900, 7200, 16500],
    [7800, 6900, 9900, 0, 17000, 12800],
    [11500, 6800, 7200, 17000, 0, 8600],
    [16200, 11700, 16500, 12800, 8600, 0]
] # km
DELAY_RATE = 1/200 # ms/km
NODE_CONFIG = [
    {
        "peer_id": 100 + i,
        "port": 8000 + i,
        "dht_port": 9000 + i,
        "connect_prob": 1,
        "region": REGIONS[i]
    }
    for i in range(NUM_NODES)
]