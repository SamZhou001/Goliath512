package main
 
import (
	"ipfs/node"
	"ipfs/bnode"
)

type Network struct {
	bnode bnode.BNode
}

func (n *Network) Init() {
	newNode := new(bnode.BNode)
	newNode.Init(10001)
	n.bnode = *newNode
}

func (n *Network) AddNode(address int) {
	newNode := new(node.Node)
	newNode.Init(address, n.bnode.GetId())
}

func main() {
	n := new(Network)
	n.Init()
	n.AddNode(10002)
}
