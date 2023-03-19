package node
 
import (
    "fmt"
	"strconv"
	"ipfs/dht"
	"context"
	"flag"
	"log"
	"net"
	"time"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	pb "ipfs/node_proto"
)

func init() {
	fmt.Println("Node package initialized")
}

type Node struct {
	peerId int
	nodeType string
	bootstrapAddr int
	dht dht.DHT
	storage string
	pb.UnimplementedNodeServiceServer
}

func (n *Node) Init(address int, bootstrapAddr int) {
	n.nodeType = "client"
	n.peerId = address
	n.dht = *new(dht.DHT)
	n.bootstrapAddr = bootstrapAddr
	n.ping()
	port := flag.Int("port", address, "The server port")
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterNodeServiceServer(s, &Node{})
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
	// Make new folder for node
}

func (n *Node) GetId() int {
	return n.peerId
}

func (n *Node) ping() {
	fmt.Println("Pinging: ", n.bootstrapAddr)
	addr := flag.String("addr", fmt.Sprint("localhost:", n.bootstrapAddr), "the address to connect to")
	conn, err := grpc.Dial(*addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewNodeServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	addressStr := strconv.FormatInt(int64(n.peerId), 10)
	r, err := c.Ping(ctx, &pb.PingRequest{Message: &addressStr})
	if err != nil {
		log.Fatalf("could not ping: %v", err)
	}
	log.Printf("Pinged: %s", r.GetMessage())
}