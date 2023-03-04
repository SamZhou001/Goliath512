package main
 
import (
	"fmt"
	"ipfs/node"
)

type Network struct {
	bnodes []node.Node
}

func (n *Network) Init(bnodeCount int) {
	for i := 0; i < bnodeCount; i++ {
		newNode := new(node.Node)
		newNode.Init(i, true)
		n.bnodes = append(n.bnodes, *newNode)
	}
}

func (n *Network) ShowState() []node.Node {
	return n.bnodes
}

func main() {
	n := new(Network)
	n.Init(5)
	fmt.Println(n.ShowState())
}
