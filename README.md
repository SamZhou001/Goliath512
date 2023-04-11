# Goliath512

## Setup for Running the Demo for David DHT
To start the David bootstrap node and 4 other nodes on ports 9000-9005:
```
docker compose up -d
```

## Running Tests
First check which nodes should get key 'CS512':
```bash
python src/examples/test_sha1.py
```
Expected Result:
```
'Key CS512 long id is 749482066561051236546021709791403608107098528806'
'For key CS512, 3 ports for the closest nodes are [9002, 9005, 9003]'
```

### Test Case 1: try setting a k,v pair using CS512 as key

```bash
python src/examples/david_set.py 0.0.0.0 9000 CS512 rocks!
```
Expected Result:
You should get successful repsonses from ports 9002, 9005, 9003 as expected.

### Test Case 2: try getting a k,v pair using CS512 as key

```bash
python src/examples/david_get.py 0.0.0.0 9000 CS512
```
Expected Result:
```
2023-04-11 07:55:31,751 - david.network - INFO - Looking up key CS512 from network
2023-04-11 07:55:31,753 - david.protocol - INFO - got successful response from 127.0.0.1:9002
2023-04-11 07:55:31,753 - david.protocol - INFO - got successful response from 127.0.0.1:9003
2023-04-11 07:55:31,753 - david.protocol - INFO - got successful response from 127.0.0.1:9005
Get result: rocks!
```

### Test Case 3: try killing and reviving nodes
For Killing
```bash
python src/examples/david_kill.py 0.0.0.0 9002
```
For Reviving
```bash
python src/examples/david_revive.py 0.0.0.0 9002
```


