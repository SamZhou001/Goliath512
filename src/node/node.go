package node
 
import (
    "fmt"
	"ipfs/dht"
)

func init() {
	fmt.Println("Node package initialized")
}

type Node struct {
	peerId int
	nodeType string
	dht dht.DHT
	peerStore []int
	storage string
}

func (n *Node) Init(address int, isBootstrap bool) {
	n.nodeType = "client"
	if (isBootstrap) {
		n.nodeType = "bootstrap"
	}
	n.peerId = address
	n.dht = *new(dht.DHT)
	// Make new folder for node
}

func (n *Node) GetId() int {
	return n.peerId
}