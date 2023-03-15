module ipfs/bnode

go 1.20

replace ipfs/dht => ../dht

replace ipfs/node => ../node

replace ipfs/node_proto => ../RPCs/ipfs/node_proto

require (
	github.com/golang/protobuf v1.5.2 // indirect
	golang.org/x/net v0.8.0 // indirect
	golang.org/x/sys v0.6.0 // indirect
	golang.org/x/text v0.8.0 // indirect
	google.golang.org/genproto v0.0.0-20230110181048-76db0878b65f // indirect
	google.golang.org/grpc v1.53.0 // indirect
	google.golang.org/protobuf v1.29.1 // indirect
	ipfs/dht v0.0.0-00010101000000-000000000000 // indirect
	ipfs/node v0.0.0-00010101000000-000000000000 // indirect
	ipfs/node_proto v0.0.0-00010101000000-000000000000 // indirect
)
