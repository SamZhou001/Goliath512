module ipfs/network

go 1.20

replace ipfs/node => ../node

replace ipfs/dht => ../dht

require (
	ipfs/dht v0.0.0-00010101000000-000000000000
	ipfs/node v0.0.0-00010101000000-000000000000
)
