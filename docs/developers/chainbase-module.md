# The `ChainBase` Module: A Deep Dive into TRON's Data Storage

## Overview

A blockchain is, in essence, an immutable distributed ledger, with its greatest value lying in solving the problem of trust. In real-world applications, blockchains are widely used for accounting and transactions. For instance, many applications leverage digital currencies like Bitcoin (BTC), Ethereum (ETH), and TRON (TRX) for economic activities to ensure the open and transparent flow of funds.

However, implementing such an immutable distributed ledger is an extremely complex systems engineering challenge, involving numerous technical domains such as P2P networking, smart contracts, databases, cryptography, and consensus mechanisms. Among these, the database, as the core component of the underlying storage, directly determines the system's performance, scalability, and data consistency, making it a critical part of blockchain architecture design.

In java-tron, the database module is called `ChainBase`. This article will focus on the `ChainBase` module, explaining the following core mechanisms:

  * [State Rollback](#rollback): How data consistency is guaranteed in scenarios like block rollbacks and chain forks.
  * [Implementation of State Rollback](#rollback-implementation): How block rollbacks are implemented.
  * [Block Persistence](#solidifying-block): How on-chain data is efficiently and reliably written to the storage engine while ensuring data consistency.

The goal is to help developers better understand the design philosophy and implementation details of `ChainBase`, enabling them to be more proficient when developing applications within the TRON ecosystem.

## Prerequisites

In a blockchain system, the database is one of the core components of the entire architecture, responsible for storing all on-chain data, including:

  * Block data
  * Transaction records
  * Contract states
  * Account information
  * Events and logs

Every TRON full node must maintain a complete copy of the data to ensure consistency across the decentralized network.

### 1\. Persistent Storage

Compared to traditional internet applications, blockchain database design has the following distinct features:

  * **High-frequency reads and writes:** A large volume of Key-Value data access occurs on the chain.
  * **Data immutability:** Once historical data is on the chain, it cannot be modified.
  * **High-performance requirements:** Transaction volumes are large, demanding extremely high read and write performance.
  * **Scalability:** The system must adapt to networks and node deployment scenarios of varying scales and support flexible expansion and storage optimization strategies.

Based on these characteristics, java-tron adopts an interface-oriented architecture in its database design. By using interface abstraction, it decouples the storage layer from the upper-level business logic. The advantage of this approach is that developers can flexibly switch between different underlying storage engines without modifying the upper-level logic.

Currently, `ChainBase` supports the following two mainstream storage engines:

  * **LevelDB:** A lightweight, embedded Key-Value store.
  * **RocksDB:** A high-performance, high-concurrency Key-Value store.

This architecture not only ensures system flexibility but also provides the capability to support more storage backends in the future.

### 2\. Transaction Validation

Before diving deep into the `chainbase` module, it is essential to first understand the transaction processing logic in java-tron.

![Transaction Validation Process](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_1.png)

Transactions are broadcast and distributed to various nodes through the network. Upon receiving a transaction, a node first verifies its signature. After successful verification, the transaction must also undergo **pre-execution** to determine its validity.

For example, for a transaction where A transfers 100 TRX to B, the system needs to verify if A has a sufficient balance. After receiving the transaction, the system will attempt to execute the balance deduction (A - 100) and addition (B + 100) in its local database. If the operation succeeds, the transaction is considered valid in the current state and can proceed to the packaging process.

<a id="rollback"></a>
## State Rollback

As mentioned earlier, java-tron uses **pre-execution** to validate the legitimacy of a transaction. However, the successful validation of a transaction on one node does not mean it has been successfully included on the chain. It has not yet been packaged into a block that has reached consensus, and therefore, there is a risk of it being rolled back.

The consensus in java-tron follows a core principle: only transactions within a block acknowledged by over 2/3 of **Super Representatives** (`SR`s) are truly successful on-chain transactions. This can be understood as:

  * The transaction is packaged into a block.
  * This block is accepted by over 2/3 of the `SR`s.

Only transactions that meet both criteria are considered successfully on-chain. In java-tron, a transaction goes through three stages to be finalized:

1.  **Transaction Validation:** Preliminary verification of the transaction's legitimacy.
2.  **Transaction Packaging into a Block:** The transaction is included in a block awaiting confirmation.
3.  **Block Reception and Application by the Majority of the Network:** The block gains enough acknowledgments from `SR`s to become a solidified block.

This raises a key question worth considering: after a node validates a transaction, it updates its local database. But if this transaction is not packaged into a block, or if the block it's in does not get confirmed by over 2/3 of the `SR`s, the node's state will be inconsistent with the rest of the network for a short period.

Therefore, **all state changes resulting from transaction processing may need to be rolled back, except for the transaction data in a block confirmed by more than two-thirds of the Super Representatives (SRs)**. The main scenarios requiring a rollback are:

  * **[After receiving a new block](#rollback-1)**, state changes from locally validated transactions must be rolled back.
  * **[After producing a new block](#rollback-2)**, state changes from transaction validation must be rolled back.
  * **[When a chain fork occurs](#rollback-3)**, blocks from the old main chain must be rolled back and blocks from the new main chain must be applied.

Let's explore each of these in detail.

<a id="rollback-1"></a>
### 1\. State Rollback Upon Receiving a New Block

When a node receives a new block, it needs to roll back its local state to what it was at the end of the previous block, undoing all state changes that resulted from transaction validations that occurred since. This is illustrated below:

![State Rollback Upon Receiving a New Block](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_2.png)

As shown in the figure:

  * At block height 100, accountA has a balance of 100.
  * The node pre-validates transaction t1: A transfers 100 to B, which executes successfully.
  * Subsequently, it receives a new block, block101, which contains transaction t2: A transfers 50 to C.
  * If t1 is not rolled back first, t2 will fail validation due to an insufficient balance.

Therefore, the changes caused by t1 must be undone, reverting the state to the end of block 100, before executing block101.

<a id="rollback-2"></a>
### 2\. State Rollback After Producing a Block

You might wonder: when producing a block, why not just package the already validated transactions directly? Why is a state rollback necessary before producing a block?

java-tron performs a **secondary validation** on transactions when packaging them into a block. The reason for this secondary validation lies in the time-sensitive nature of transactions. Using the same example, after receiving block 101, transaction `t1` was rolled back, and `accountA`'s balance was reduced by 50. When it's this node's turn to produce a block, `t1` has now become an invalid transaction because `accountA`'s balance is no longer sufficient to cover the 100 TRX transfer. It would be incorrect to package `t1` into the new block, so the transaction must be re-validated. This is why the state must be rolled back before block production.

After a block is successfully packaged, the node broadcasts it to the network and also `apply`s it locally. The `apply` logic will re-validate the transactions within the block. Therefore, even after packaging a block, a rollback operation is still necessary.

<a id="rollback-3"></a>
### 3\. State Rollback for Forked Chains

Forks are an unavoidable occurrence in blockchain operation, especially in systems based on the DPoS consensus mechanism, which have fast block production times. When multiple candidate chains appear in the network, the system must choose one as the main chain according to consensus rules, while the other chains are rolled back and discarded.

To achieve this, java-tron maintains a specific data structure in memory (as shown below) to track the current main chain, forked chains, and their corresponding state information.

![State Rollback for Forked Chains](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_3.png)

java-tron keeps all recent, not-yet-finalized blocks in memory. When a fork occurs, the system uses the **longest chain rule** to select the main chain: if a forked chain's block height surpasses that of the current main chain, the forked chain will become the new main chain.

The switching process is as follows:

  * Find the **common parent block** (i.e., the fork point) of the two chains.
  * Roll back from the current main chain to the parent block, sequentially removing the main chain blocks that came after it.
  * Starting from the parent block, `apply` the block data from the new main chain in order.

As shown in the figure above, the red `Fork A` was originally the main chain. However, as `Fork B`'s height continued to grow, it eventually surpassed `Fork A`. At this point, the system will roll back blocks 103, 102, and 101 from `Fork A` and then sequentially `apply` blocks 101, 102, 103, and 104 from `Fork B`.

<a id="rollback-implementation"></a>
## Implementation of State Rollback

This section will explain the processes of transaction reception, transaction validation, block generation, block validation, and block saving from a code-level perspective to further analyze the `chainbase` module.

### 1\. Transaction Reception

![Transaction Reception Process](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_4.png)

  * When a node receives a broadcasted transaction, it accepts it through the `Manager.pushTransaction(final TransactionCapsule trx)` function: the transaction is placed in the local `pushTransactionQueue` cache, and simultaneously, it is validated.
  * After passing validation, the transaction moves to the `pendingTransactionQueue`, to be used during block production.
  * If the node is an SR, it will pull transactions from this queue to build a block.

Handling Validation Failures:

  * From API: Return an exception message to the user.
  * From P2P Network: Log the error locally.

### 2\. State Rollback When a New Block is Received

Before a new block arrives, a node may have already received broadcasted transactions and validated them. The validation process temporarily modifies the node's state to determine if the transaction can be executed correctly.

However, successful validation does not guarantee that the transaction will ultimately take effect, as it still needs to be packaged into a block and solidified. To ensure state consistency, when a new block arrives, the node rolls back the temporary state changes caused by transaction validation, retaining only the state changes generated during the block application process.

![State Rollback When a New Block is Received](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_5.png)

During the rollback, transactions from the `pendingTransactionQueue` must be moved to `rePushTransactions`, and the `pendingTransactionQueue` must be cleared. Please refer to the diagram above for a detailed explanation.

Why is the `pendingTransactionQueue` cleared when a new block arrives? First, it's important to understand that the `pendingTransactionQueue` is responsible for providing transactions during block generation; it holds validated transactions ready for packaging. However, since the new block also alters account states, it might invalidate transactions in the `pendingTransactionQueue` that were previously validated. (A simple example: a transaction in the new block has account A spend some tokens, causing a subsequent transaction from account A in the queue to have an insufficient balance). After moving the transactions to `rePushTransactions`, a background thread is responsible for re-validating the transactions in that queue. If they are still valid, they are moved back to the `pendingTransactionQueue` to be available for block production.

java-tron uses a `session` object, where one `session` represents the state changes caused by one block. The `session` object is primarily used for rollbacks, such as reverting the state to that of the previous block, as shown below:

![Session Object and Databases](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_6.png)

The figure shows that the persistent storage contains various types of databases, which together form a complete blockchain. For example, blocks are stored in `khasodb` and `blockStore`, while account information is stored in `accountStore`.

A node maintains a linked list of `session`s, which stores the change information corresponding to blocks/transactions, allowing the node to revert using this information. In the figure, `session1` represents the state changes from the current highest block. When a transaction is received, a new `session2` is created. For each subsequent transaction received, a temporary `tmpSession` is generated. After the transaction is validated, `tmpSession` is immediately merged into `session2`. Before a new block arrives, all state changes from transaction validations are saved in `session2`. When a new block arrives, simply calling the `reset` method on `session2` will roll the state back to that of the previous block.

### 3\. State Rollback When Producing a Block

The reason an `SR` needs to roll back before producing a block is somewhat complex. Let's consider a scenario:

  * The `pendingTransactionQueue` contains currently validated transactions. So, when an `SR` node produces a block, it could simply package transactions from the `pendingTransactionQueue`, and after packaging, roll back the state to that of the previous block.

However, this approach has a problem: if the `SR` node has just received and `apply`ed a new block, we know from the previous section that `pendingTransactionQueue` will be cleared and its contents moved to `rePushTransactions`. If it's this SR's turn to produce a block right at that moment, its `pendingTransactionQueue` might not have enough transactions. Therefore, the actual implementation is that during block production, transactions are read not only from `pendingTransactionQueue` but also from `rePushTransactions` if the former has few transactions. And as we've analyzed, transactions in `rePushTransactions` may no longer be valid, so they need to be re-validated. It is this validation logic that necessitates a state rollback before producing a block.

![State Rollback When Producing a Block](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_7.png)

During block production, transactions are validated again, which causes state changes. But this is just block generation; the block still needs to be broadcast. Only the reception of a broadcasted block truly changes the state. Therefore, the state changes produced during block generation also need to be rolled back. As shown in the figure above, after block production is complete, `session2''` must also be rolled back.

<a id="solidifying-block"></a>
## Block Persistence

java-tron uses a DPoS consensus mechanism, where 27 Super Representatives (SRs) are elected through voting to serve as block producers, responsible for producing and confirming blocks.

When a block receives acknowledgment from over 2/3 of the SRs—meaning more than 2/3 of the Super Representatives have produced subsequent blocks based on it—the block is considered to have reached consensus and will no longer be rolled back. This is called a **Solidified Block**. Only solidified blocks are safely written to the database.

In the `Chainbase` module, the `SnapshotManager` plays a central role. It acts as a unified entry point to the storage layer, managing and maintaining references to all business databases. These database references are stored in a list, and each database instance supports adding a temporary state set on top of itself, known as a `SnapshotImpl`.

A `SnapshotImpl` is essentially an in-memory `HashMap`. Multiple `SnapshotImpl`s are linked together in a list structure. Each `SnapshotImpl` independently saves the data modifications related to a single state change, isolated from the others. This chained snapshot structure allows the system to manage and control rollbacks for different states independently, as shown below:

![SnapshotManager Structure](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_8.png)

In the figure, `SnapshotRoot` is a wrapper class for the underlying persistent database, responsible for storing all solidified data.

We previously mentioned the concept of a `session`: one `session` represents the global state changes caused by a block. In reality, a `session` is composed of multiple `SnapshotImpl`s corresponding to different databases. For example, in the diagram, all the `SnapshotImpl`s corresponding to block 5 together form the set of state changes for block 5.

When a node receives a new block, its state changes are not immediately written to persistent storage. Instead, they are first recorded in an in-memory `SnapshotImpl`. A new `SnapshotImpl` is generated for each received block. As blocks continue to arrive, the number of `SnapshotImpl`s grows.

So, when are these in-memory snapshots (`SnapshotImpl`) actually written to persistent storage?

There are two key variables in `SnapshotManager`:

  * `size`: Represents the current number of `SnapshotImpl` layers in memory.
  * `maxSize`: Represents the difference between the solidified block height and the latest block height.

When `size` \> `maxSize`, it means that the first `size - maxSize` layers of `SnapshotImpl`s correspond to blocks that are now solidified and can be safely flushed to disk. At this point, `SnapshotManager` writes these `SnapshotImpl`s to the persistent database.

This mechanism prevents the infinite accumulation of `SnapshotImpl`s, which would lead to excessive memory consumption, while also ensuring that solidified blocks are written to the database in a timely and reliable manner.

### 1\. Database Atomicity

The database storage design of java-tron differs from that of other public chains. Ethereum uses a single database instance at the persistence layer, distinguishing different data types with prefixes and storing everything in the same database. In contrast, java-tron adopts a **multi-database instance** design, storing data for different business logic in separate database instances.

Both approaches have their pros and cons:

  * **Single-instance database:**
      * **Pros:** Simple maintenance, unified data writing.
      * **Cons:** The single database can grow continuously over time; high-frequency access to certain business data might affect the read/write performance of other services.
  * **Multi-instance database:**
      * **Pros:** Data for different business logic does not interfere with each other. Parameters can be configured independently for databases with different data scales and access patterns, allowing for performance optimization. Large databases can also be split off to mitigate bloating issues.
      * **Cons:** Lacks native support for atomic writes across databases, which introduces challenges for transactional consistency.

To address the lack of atomic write support in a multi-database setup, java-tron introduces a **checkpoint mechanism**. Before writing data to multiple database instances, the system first records all data to be written into a `checkpoint`. If an exception occurs during the writing process, the node can restore a consistent data state from the `checkpoint` upon restart, thereby guaranteeing atomicity for the multi-instance writes.

As mentioned in the previous section, the `SnapshotImpl`s corresponding to solidified blocks must eventually be written to the database. This process is divided into two main steps:

1.  **Create a `checkpoint`**
    The `SnapshotImpl`s in memory that need to be flushed to disk are first persisted to a temporary database, `tmp`.
2.  **Perform the disk-writing operation**
    Only after the `checkpoint` is successfully created will the system formally write the corresponding `SnapshotImpl`s to their respective business database instances.

During the multi-instance database write process, creating the `checkpoint` is a critical step. The purpose of the `checkpoint` is to first persist all the `SnapshotImpl`s from memory that are waiting to be written into a single temporary database (the `tmp` database) before the data is actually flushed to disk.

Only after the `checkpoint` is successfully created does the system proceed with the operation of flushing the `SnapshotImpl`s to disk. If the node unexpectedly crashes during this flushing process, upon restart, the system will first check for the existence of `checkpoint` data in `tmp`:

  * If it exists, the data from the `checkpoint` will be replayed into the `SnapshotRoot`, thus restoring a consistent database state.
  * If it does not exist, it means the previous data was safely flushed to disk, and the node can continue its operations normally.

The data structure of the `checkpoint` is as follows:

![image](https://raw.githubusercontent.com/tronprotocol/documentation-en/master/images/chainbase_9.png)

The `checkpoint` stores all data related to a single state change in a temporary database, using prefixes to distinguish between different data types. To ensure that all data is completely written, the underlying database's `writeBatch()` method is used for atomic batch writes.

The core idea of this mechanism can be summarized as:

  * There is no guarantee of atomic writes across multiple database instances, but single-instance databases (most mainstream ones) typically support atomic writes.
  * Therefore, the system first writes the dataset requiring atomic operations to a temporary database (guaranteeing atomicity), and then distributes the data from the temporary database to the individual database instances.
  * If an exception occurs during the writing process, the node can rely on the data in the temporary database for recovery, thus ensuring the consistency and reliability of the overall write operation.

## Conclusion

This article, in conjunction with the transaction and block processing flows, has analyzed the implementation mechanisms of the `ChainBase` module concerning "State Rollback" and "Database Writing". It has also highlighted java-tron's `checkpoint` atomic write solution, introduced specifically for multi-database instance writing, and how it effectively prevents database corruption in the event of unexpected situations like a crash. We hope this article helps developers gain a deeper understanding and participate more effectively in the development and optimization of the java-tron database.