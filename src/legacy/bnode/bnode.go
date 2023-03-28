package bnode
 
import (
    "fmt"
	"strconv"
	"context"
	"flag"
	"log"
	"net"
	"google.golang.org/grpc"
	pb "ipfs/node_proto"
)

func init() {
	fmt.Println("BNode package initialized")
}

type BNode struct {
	peerId int
	peerStore []int
	lastPinged []int
	pb.UnimplementedNodeServiceServer
}

func (n *BNode) Init(address int) {
	n.peerId = address
	port := flag.Int("port", address, "The server port")
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterNodeServiceServer(s, &BNode{})
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func (n *BNode) GetId() int {
	return n.peerId
}

func (n *BNode) Ping(ctx context.Context, in *pb.PingRequest) (*pb.PingReply, error) {
	addr, err := strconv.Atoi(*in.Message)
	if err != nil {
		log.Fatalf("invalid ping message: %v", err)
	}
	if (!contains(n.peerStore, addr)) {
		n.peerStore = append(n.peerStore, addr)
	}
	if (!contains(n.lastPinged, addr)) {
		n.lastPinged = append(n.lastPinged, addr)
	}
	fmt.Println("Received ping")
	return &pb.PingReply{}, nil
}

func contains(s []int, val int) bool {
	for _, v := range s {
		if v == val {
			return true
		}
	}
	return false
}