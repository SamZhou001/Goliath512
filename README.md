# Goliath512

## Setup for Running the Demo for David DHT
To start the David bootstrap node and 9 other nodes on ports 9000-9009:
```
docker compose up -d
```

## Running Tests
First check which nodes should get key 'cs512':
```bash
python src/examples/test_sha1.py
```
Expected Result:
```
'Key cs512 long id is 805593505797178145315964510806761305491604746615'
For key cs512, 10 ports for the closest nodes are [9006, 9005, 9002, 9003, 9004, 9009, 9001, 9007, 9008, 9000]
```

### Test Case 1: try setting a k,v pair using cs512 as key

```bash
python src/examples/david_set.py cs512 rocks!
```
Expected Result:
You should get successful repsonses from ports 9006, 9005, 9002, 9003, 9004 as expected.

### Test Case 2: try getting a k,v pair using cs512 as key

```bash
python src/examples/david_get.py cs512
```
Expected Result:
```
2023-04-11 07:55:31,751 - david.network - INFO - Looking up key CS512 from network
2023-04-11 07:55:31,753 - david.protocol - INFO - got successful response from 127.0.0.1:9006
2023-04-11 07:55:31,753 - david.protocol - INFO - got successful response from 127.0.0.1:9005
2023-04-11 07:55:31,753 - david.protocol - INFO - got successful response from 127.0.0.1:9002
Get result: rocks!
```

### Test Case 3: try killing and reviving nodes
For Killing
```bash
python src/examples/david_kill.py 0.0.0.0 9006
```
For Reviving
```bash
python src/examples/david_revive.py 0.0.0.0 9006
```


