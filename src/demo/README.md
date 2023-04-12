Commands:
Open 4 terminals.
In terminal 1 (creates server at port 8000): `python examples/david_node.py` 
In terminal 2 (creates server at port 8469): `python examples/david_node.py -i 0.0.0.0 -p 8000`
In terminal 3 (creates server at port 8472): `python examples/david_node2.py -i 0.0.0.0 -p 8000`
In terminal 4: 
`python examples/david_set.py 0.0.0.0 8469 hi jerry3` (creates temporary server at port 8470)
`python examples/david_get.py 0.0.0.0 8000 hi` (creates temporary server at port 8471)


