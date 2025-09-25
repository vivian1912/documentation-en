# TRON's P2P Network Architecture and Core Mechanisms

At the heart of the TRON network lies its efficient, decentralized **P2P (Peer-to-Peer) network** architecture. As the foundational layer of the TRON blockchain, the design and implementation of the P2P network directly determine the stability and performance of the entire system. This document provides an in-depth analysis of the four core functions of the TRON P2P network: node discovery, node connection, block synchronization, and block and transaction broadcasting.


## P2P Network Overview

A P2P network is a type of distributed network where participants directly share hardware resources such as computing power, storage, and network connections without relying on a central server. In a P2P network, each node is both a provider and a consumer of information, a model that significantly enhances resource utilization and network robustness.

### Blockchain and P2P

P2P constitutes the **network layer** in the blockchain architecture. It provides the foundation for decentralized information dissemination, verification, and communication among nodes. Each node maintains a copy of the shared blockchain data to stay synchronized, thereby ensuring network-wide consensus.

This decentralized P2P architecture offers significant advantages to the TRON network:

  * **Prevents Single Points of Attack**: The network has no central point of failure.
  * **High Fault Tolerance**: The network can continue to operate even if some nodes go offline.
  * **Good Scalability**: The network's ability to expand is not limited by a central server.

The TRON architecture is illustrated below:

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_architecture.png)

The P2P module of the TRON network can be divided into the following four main functions:

1.  [Node Discovery](#node-discovery)
2.  [Node Connection](#node-connection)
3.  [Block Synchronization](#block-sync)
4.  [Block and Transaction Broadcasting](#broadcasting)

<a id="node-discovery"></a>
## Node Discovery

Node discovery is the first step for a new node to join the TRON network. TRON employs a structured P2P network based on the **Kademlia algorithm**. This algorithm allows nodes to quickly and efficiently find other nodes without a central directory.

### Kademlia Algorithm Principles

Kademlia is a Distributed Hash Table (**DHT**) implementation that organizes its routing table by calculating the "distance" between nodes using the XOR metric of their IDs.

Key aspects of TRON's Kademlia implementation include:

  * **Node ID**: Each node generates a random 512-bit ID upon startup.
  * **Node Distance**: The distance between two nodes is calculated by performing an XOR operation on their IDs. The formula is: `Distance = 256 - number of leading zeros in the XOR result of the Node IDs`. If the result is negative, the distance is 0.
  * **K-bucket**: This is the node's routing table, used to store information about remote nodes. Remote nodes are organized into 256 "buckets" based on their distance from the local node, with each bucket holding a maximum of 16 nodes.

### Node Discovery Protocol Messages

The TRON node discovery protocol is based on **UDP** and uses the following four message types for communication:

  * `DISCOVER_PING`: Used to check if a target node is online.
  * `DISCOVER_PONG`: The response to a `DISCOVER_PING` message.
  * `DISCOVER_FIND_NODE`: Used to find nodes closest to a specific target ID.
  * `DISCOVER_NEIGHBORS`: The response to a `DISCOVER_FIND_NODE` message, returning up to 16 nodes.

### Node Discovery Process

#### 1\. Initialize K-buckets

Upon startup, a node reads the `seed nodes` from its configuration file and known peers from its database. It sends `DISCOVER_PING` messages to them. If it receives a `DISCOVER_PONG` response, it adds the responding node to the appropriate K-bucket. If the K-bucket is full, it will challenge the oldest node in the bucket and replace it with the new node upon success.

#### 2\. Periodically Discover More Nodes

The TRON node discovery service periodically runs two scheduled tasks to continuously update its K-buckets:

  * **`DiscoverTask`**: Runs every **30 seconds** to discover more nodes that are closer to the local node. The process is shown in the figure below:
![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_discovertask.png)
  * **`RefreshTask`**: Runs every **7.2 seconds** to expand the local K-buckets by searching for nodes closest to a random ID. The process is shown in the figure below:
![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_refreshtask.png)

Each time these tasks run, they execute eight rounds of node discovery. In each round, a `DISCOVER_FIND_NODE` message is sent to the **3** nodes in the K-bucket closest to the target ID to request more neighbors.

#### 3\. Receive and Update K-buckets

When a node receives a `DISCOVER_NEIGHBORS` message from a remote node, it sequentially sends `DISCOVER_PING` messages to the neighbors in the response. If it successfully receives a `DISCOVER_PONG` response, the node attempts to add this new node to the corresponding K-bucket. If the K-bucket is full, it will challenge a node in the bucket (by sending a `DISCOVER_PING`). If the challenge is successful (i.e., no `PONG` response is received), the old node is removed, and the new node is added.

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_updatek.png)

Through these periodic tasks, each node continuously builds and maintains a dynamic and healthy routing table.


<a id="node-connection"></a>
## Node Connection

After discovering potential nodes, the next step is to establish **TCP connections**. The TRON network categorizes nodes to manage connections efficiently and stably.

### Node Classification

TRON nodes classify their peers into the following categories:

  * **Active Nodes**: Specified in the configuration file. The node will proactively attempt to connect to them upon startup. If a connection fails, it will retry in every scheduled TCP connection task.
  * **Passive Nodes**: Specified in the configuration file. The node will passively accept connection requests from these nodes.
  * **Trust Nodes**: Includes both `Active` and `Passive` nodes. TRON prioritizes these nodes and may skip certain connection checks.
  * **Bad Nodes**: Nodes that have been blacklisted. When a node sends an abnormal protocol message, it is marked as a `badNode` for a period of **1 hour**.
  * **Recently Disconnected Nodes**: Nodes that have disconnected within the last 30 seconds, to prevent rapid reconnection attempts.

### Establishing TCP Connections

A TRON node periodically runs a scheduled task named `poolLoopExecutor` to establish TCP connections. Its workflow is as follows:

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_connect.png)

1.  **Determine Connection List**: First, it checks for any `active nodes` that are not yet successfully connected and adds them to the list.
2.  **Filter Neighbor Nodes**: It calculates the number of additional connections needed and selects the best nodes from the discovered neighbors list based on the **node filtering strategy** and **node scoring strategy**.
3.  **Establish Connections**: It initiates TCP connections to the nodes in the final list.

#### 1\. Node Filtering Strategy

Before attempting a connection, the node filters out unqualified candidates, including:

  * The node itself.
  * Nodes in the `recentlyDisconnectedNodes` or `badNodes` lists.
  * Nodes that are already connected.
  * Nodes from an IP that has reached the connection limit (`maxConnectionsWithSameIp`).

> **Note**: `trust nodes` bypass some filtering rules and are always prioritized for connection.

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_filterrule.png)

#### 2\. Node Scoring Strategy

Nodes are scored based on multiple criteria to determine connection priority. The higher the score, the higher the priority.

| Dimension | Scoring Rule |
| :--- | :--- |
| **Packet Loss Rate** | The lower the packet loss rate, the higher the score. Max **100** points. |
| **Network Latency** | The lower the latency, the higher the score. Max **20** points. |
| **TCP Traffic** | The higher the traffic, the higher the score. Max **20** points. |
| **Number of Disconnections** | The more disconnections, the lower the score (negative points). Each disconnection deducts **10** points. |
| **Successful Handshakes** | A node that has successfully handshaken before gets **20** points; otherwise, **0**. |
| **Penalty Status** | If a node is in a penalty state (e.g., disconnected less than 60 seconds ago, on the `badNodes` list, inconsistent chain info), it scores **0** points immediately. |

### Handshake and Keep-Alive

Once a TCP connection is successfully established, the two nodes perform a handshake by exchanging `P2P_HELLO` messages to verify each other's blockchain information (e.g., `p2p version`, `genesis block`). If all checks pass, the handshake is successful, and the connection proceeds to the block synchronization or data broadcasting stage. Otherwise, the connection is terminated.

To keep the channel active, nodes periodically send `P2P_PING` messages. If a `P2P_PONG` response is not received within a timeout period, the connection is dropped.

<a id="block-sync"></a>
## Block Synchronization

After a new node successfully connects and handshakes, if it discovers that a remote peer's blockchain is longer than its own, it will trigger the block synchronization process, `syncService.startSync`, based on the longest chain principle. The message exchange during synchronization is shown below:

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_syncflow.png)

1.  **Request Chain Summary**: Node A sends a `SYNC_BLOCK_CHAIN` message to Node B, containing a summary of its local chain (e.g., highest solidified block, highest unsolidified block).
2.  **Return Missing Inventory**: Upon receiving the summary, Node B compares it with its own chain, calculates a list of block IDs that Node A is missing, and sends it back in a `BLOCK_CHAIN_INVENTORY` message. Each message can carry up to **2000** block IDs.
3.  **Request Missing Blocks**: After receiving the inventory, Node A asynchronously requests the missing blocks using a `FETCH_INV_DATA` message, requesting up to **100** blocks at a time. If more blocks remain, a new synchronization round is triggered.
4.  **Send Blocks**: Node B receives the `FETCH_INV_DATA` request and sends the block data to Node A via `BLOCK` messages.
5.  **Process**: Node A receives the `BLOCK` message and processes the block asynchronously.

### Chain Summary and Missing Block Inventory

During block synchronization, nodes use a **chain summary** and a **missing block inventory** to determine which blocks to fetch.

  * **Chain Summary**: Composed of an ordered set of block IDs, typically including the highest solidified block, the highest unsolidified block, and intermediate blocks selected via a binary search approach.
  * **Missing Block Inventory**: The neighbor node compares the chain summary with its own chain to identify the missing blocks and returns a list of consecutive block IDs and the count of remaining blocks.

Below are several examples illustrating how the chain summary and missing block inventory are generated in different synchronization scenarios.

#### Normal Scenario

The local head block height is **1018**, and the solidified block height is **1000**.
Since this is the first connection between Node A and Node B, the common block height is **0**.
Node A generates a chain summary via binary search: `1000, 1010, 1015, 1017, 1018`.

Node B receives the summary, compares it with its own chain, and finds that Node A is missing blocks: `1018, 1019, 1020, 1021`.
Subsequently, Node A uses the missing block inventory to request synchronization for `1019, 1020, 1021`.

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_sync1.png)


#### Chain Fork Scenarios

**Scenario 1**
The local main chain head block height is **1018**, the solidified block height is **1000**, and the common block height is **0**.
Node A's chain summary is: `1000, 1010, 1015, 1017, 1018`.

Node B receives the summary, detects a chain fork, and after comparison, confirms the common block is **1015**.
Therefore, the missing block inventory for Node A is: `1015, 1016', 1017', 1018', 1019'`.
Node A then requests to sync `1018', 1019'`.

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_sync2.png)

**Scenario 2**
The local main chain head block height is **1018**, the solidified block height is **1000**, and the common block height is **1017'** (on the fork).
Node A's chain summary is: `1000, 1009, 1014, 1016', 1017'`.

Node B compares the summaries and generates a missing block inventory: `1017', 1018', 1019'`.
Node A then requests to sync `1018', 1019'`.

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_sync3.png)


<a id="broadcasting"></a>
## Block and Transaction Broadcasting

When a Super Representative node generates a new block, or when a node receives a new transaction, it initiates a broadcast process. The broadcasting and forwarding flows are largely identical. The message exchange is illustrated below:

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/network_broadcastflow.png)

The message types involved include:

  * `INVENTORY`: A broadcast list containing block or transaction IDs.
  * `FETCH_INV_DATA`: A request to fetch the data listed in the inventory.
  * `BLOCK`: Block data.
  * `TRXS`: Transaction data.

The specific process is as follows:

1.  **Send Inventory**: Node A packages the IDs of the block or transactions to be broadcast into an `INVENTORY` message and sends it to its neighbor, Node B.
2.  **Place in Queue**: When Node B receives the `INVENTORY`, it checks the status of Node A. If the message can be accepted, it places the block/transaction IDs from the inventory into a fetch queue called `invToFetch`. If it is a block inventory, it immediately sends a `FETCH_INV_DATA` message to request the data.
3.  **Send Data**: Upon receiving `FETCH_INV_DATA`, Node A verifies that it has previously sent an inventory message to Node B. If so, it sends the specific block (`BLOCK`) or transaction (`TRXS`) data corresponding to the inventory.
4.  **Process and Forward**: After receiving the data, Node B processes and validates it, then triggers a forwarding process to broadcast it to its own neighbors.


## Conclusion

This article has provided a detailed overview of the underlying implementation of the TRON P2P network, covering the core mechanisms of node discovery, connection, block synchronization, and data broadcasting. Through a deep understanding of these modules, developers can better appreciate the robustness and efficiency of the `java-tron` network and build upon this foundation for further development and optimization.