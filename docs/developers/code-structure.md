# Java-tron Module Structure

`Java-tron` is the core client of the TRON network, written in Java. It implements all the core functionalities defined in the TRON whitepaper, including the consensus mechanism, cryptographic algorithms, database management, the TRON Virtual Machine (TVM), and network communication. Developers can quickly run a TRON network node by launching Java-tron.

This article will systematically analyze the code structure of Java-tron, providing an in-depth look at the responsibilities and organization of each functional module to serve as a reference for developers for future source code analysis and functional extensions.

`Java-tron` adopts a modular design philosophy, ensuring the code's clarity, maintainability, and extensibility. Currently, `Java-tron` consists of the following seven core modules:

  * [protocol](#protocol-module)
  * [common](#common-module)
  * [chainbase](#chainbase-module)
  * [consensus](#consensus-module)
  * [actuator](#actuator-module)
  * [crypto](#crypto-module)
  * [framework](#framework-module)

Next, we will introduce the functions and internal structures of these modules one by one.

## `protocol` Module

In a distributed network environment like a blockchain, concise and efficient data interaction protocols are crucial. The `protocol` module defines the key communication protocols within the `java-tron` client:

  * Communication protocols between nodes
  * Communication protocols between internal modules of a node
  * Service protocols exposed to external clients

These protocols uniformly use [`Google Protobuf`](https://developers.google.com/protocol-buffers) (Protocol Buffers) as the data interchange format. Compared to JSON and XML, Protobuf offers advantages such as smaller size, faster parsing, and better type safety, while also providing excellent structure definition capabilities and extensibility. With the help of the Protobuf compiler, serialization and deserialization code can be automatically generated for multiple languages (such as Java, C++, Python, etc.) based on the defined protocol files, facilitating cross-language integration. Protobuf is the core foundation for `java-tron`'s cross-platform, cross-language communication, supporting efficient data transmission between nodes, between modules, and for external service interfaces.

The source code for the `protocol` module is located in the [protocol directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/protocol). Its core directory structure is as follows:

```
|-- protos
    |-- api
    |   |-- api.proto
    |-- core
        |-- Discover.proto
        |-- Tron.proto
        |-- TronInventoryItems.proto
        |-- contract
```

  * `protos/api/`: Defines the gRPC interfaces and related data structures exposed by a `java-tron` node.
  * `protos/core/`: Defines the data structures required for communication between nodes and between internal modules of a node.
      * `Discover.proto`: Defines data structures related to the node discovery mechanism.
      * `TronInventoryItems.proto`: Defines data structures related to block and transaction transmission between nodes.
      * `contract/`: Defines data structures related to smart contracts.
      * `Tron.proto`: Defines other important core data structures, including those for accounts, blocks, transactions, resources (such as **Bandwidth** and **Energy**), Super Representatives, voting, and proposals.

## `common` Module

The `common` module encapsulates commonly used public components and utility classes in `java-tron`, aiming to enhance code reusability and allow for uniform invocation by other modules. This module contains general-purpose functionalities like exception handling mechanisms and metrics monitoring tools.

The source code is located in the [common directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/common), and its core directory structure is as follows:

```
|-- /common/src/main/java/org/tron
    |-- common
    |   |-- args
    |   |-- cache
    |   |-- config
    |   |-- cron
    |   |-- entity
    |   |-- es
    |   |-- exit
    |   |-- log
    |   |-- logsfilter
    |   |-- math
    |   |-- parameter
    |   |-- prometheus
    |   |-- runtime/vm
    |   |-- setting
    |   |-- utils
    |-- core
        |-- config
        |-- db
        |-- db2
        |-- exception
        |-- vm/config
        |-- Constant.java
```

  * `common/prometheus`: Integrates the Prometheus metrics monitoring tool to collect and expose runtime metrics of the `java-tron` node for system monitoring and performance analysis.
  * `common/utils`: Provides a series of wrapper classes for basic data types and utility methods (e.g., data conversion, formatting) to improve development efficiency and code readability.
  * `core/config`: Contains classes related to node configuration, responsible for managing and loading various runtime parameters of the `java-tron` node.
  * `core/exception`: Defines the exception handling mechanism for the TRON network, supporting unified error catching and feedback to enhance system robustness and maintainability.
  * `common/args`: Classes for defining basic node parameters.
  * `common/cache`: Classes related to database caching.
  * `common/config`: Configuration classes for database backups.
  * `common/es`: Service execution manager.
  * `common/cron`: Cron expression handling classes.
  * `common/entity`: Defines node and peer information.
  * `common/exit`: Service exit management classes.
  * `common/log`: Logging services.
  * `common/logsfilter`: Event plugin configuration classes and various event definition classes.
  * `common/math`: Wrapper classes for mathematical calculations.
  * `common/parameter`: Configuration classes for node startup parameters.
  * `common/runtime/vm`: Classes for handling TVM field types.
  * `common/setting`: RocksDB configuration classes.
  * `core/db` and `core/db2`: Basic classes related to the database.

## `chainbase` Module

The `chainbase` module is `java-tron`'s abstraction layer for the database. Considering the possibility of chain forks in probability-based consensus algorithms like Proof of Work (PoW), Proof-of-Stake (PoS), and Delegated Proof-of-Stake (DPoS), `chainbase` provides a database interface standard that supports state rollbacks. This interface requires the underlying database to implement capabilities such as a state rollback mechanism and a Checkpoint disaster recovery mechanism to ensure data consistency and reliability when a chain reorganization occurs.

Additionally, the `chainbase` module features a well-designed interface abstraction, allowing any database that conforms to this interface specification to serve as the underlying storage for the blockchain system, thereby providing developers with greater flexibility. Currently, `java-tron` provides two default implementations: LevelDB and RocksDB.

The source code for the chainbase module is located in the [chainbase directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/chainbase), with the following core directory structure:

```
|-- chainbase.src.main.java.org.tron
    |-- common
    |   |-- bloom
    |   |-- error
    |   |-- overlay/message
    |   |-- runtime
    |   |-- storage
    |   |   |-- leveldb
    |   |   |-- rocksdb
    |   |-- utils
    |-- core
        |-- actuator
        |-- capsule
        |-- config/args
        |-- db
        |   |-- RevokingDatabase.java
        |   |-- TronStoreWithRevoking.java
        |   |-- ......
        |-- db2
        |   |-- common
        |   |-- core
        |       |-- SnapshotManager.java
        |       |-- ......
        |-- net/message
        |-- service
        |-- store
        |-- ChainBaseManager.java
```

  * `common/`: Encapsulates some common components, such as exception handling classes and utility classes.
      * `storage/leveldb/`: Database storage logic implemented based on LevelDB.
      * `storage/rocksdb/`: Database storage logic implemented based on RocksDB.
  * `core/`: The core code of the `chainbase` module.
      * `capsule/`: Encapsulates various core data structures (e.g., `AccountCapsule`, `BlockCapsule`) to provide read/write interfaces for objects like accounts and blocks.
      * `store/`: Implements various business-specific databases (e.g., `AccountStore` and `ProposalStore`).
          * `AccountStore`: Account database, named `account`, used to store all account information.
          * `ProposalStore`: Proposal database, named `proposal`, used to store all proposal information.
      * `db/` and `db2/`: Implements the revokable database.
          * `db/`: Contains the early `AbstractRevokingStore`.
          * `db2/`: Contains the more stable and extensible `SnapshotManager`. It is the main rollback mechanism implementation currently in `java-tron`. Key classes and interfaces include:
              * `RevokingDatabase.java`: A database container interface responsible for managing all revokable databases. `SnapshotManager` is a concrete implementation of this interface.
              * `TronStoreWithRevoking.java`: A generic base class for databases that support the rollback mechanism. Specific business databases like `BlockStore` and `TransactionStore` are implemented based on this class.

## `consensus` Module

The consensus mechanism is a crucial core module in a blockchain system; it determines how nodes in the network reach an agreement on the validity of transactions and blocks. Common consensus algorithms include Proof of Work (PoW), Proof of Stake (PoS), Delegated Proof of Stake (DPoS), and Practical Byzantine Fault Tolerance (PBFT). In consortium chains or permissioned networks, consistency algorithms like Paxos and Raft are also commonly used.

The choice of a consensus mechanism should match the specific business scenario. For example, real-time games that are sensitive to consensus efficiency are not suitable for PoW, whereas PBFT might be the preferred choice for exchanges with extremely high real-time requirements. Therefore, supporting pluggable consensus mechanisms is essential, and it is also a vital part of implementing application-specific blockchains. The ultimate goal of the `consensus` module is to allow application developers to switch consensus mechanisms as easily as configuring a parameter.

The source code for the `consensus` module is located in the [consensus directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/consensus), with the following core directory structure:

```
|-- consensus/src/main/java/org/tron/consensus
    |-- Consensus.java
    |-- ConsensusDelegate.java
    |-- base
    |   |-- ConsensusInterface.java
    |   |-- ......
    |-- dpos
    |-- pbft
```

The `consensus` module abstracts the consensus process into a set of core interfaces, uniformly defined in `ConsensusInterface`, which mainly includes the following methods:

  * `start`: Starts the consensus service, supporting custom startup parameters.
  * `stop`: Stops the consensus service.
  * `receiveBlock`: Defines the consensus processing logic for when a block is received.
  * `validBlock`: Defines the consensus logic for block validation.
  * `applyBlock`: Defines the processing logic for applying a block (writing to the state).

Currently, `java-tron` provides two implementations of this interface: DPoS (in the `dpos/` directory) and PBFT (in the `pbft/` directory).

Developers can also implement the `ConsensusInterface` according to their specific business needs to integrate other consensus algorithms, enabling more flexible chain design and deployment.

## `actuator` Module

Ethereum pioneered the introduction of the virtual machine and the smart contract development paradigm, greatly advancing the development of blockchain applications. However, in some complex scenarios, smart contracts still have limitations in terms of flexibility and performance. To meet the demand for higher performance and customization, `java-tron` provides the ability to build Application Chains and has designed the independent `actuator` module for this purpose.

The `actuator` module is the executor for transactions. It supports embedding application logic directly into the chain without running it in a virtual machine. Developers can view an application as being composed of different types of transactions, with each transaction type corresponding to a dedicated actuator responsible for its specific execution logic. This allows for highly customized on-chain processing capabilities.

The source code for the `actuator` module is located in the [actuator directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/actuator). Its core directory structure is as follows:

```
|-- actuator/src/main/java/org/tron/core
    |-- actuator
    |   |-- AbstractActuator.java
    |   |-- ActuatorCreator.java
    |   |-- ActuatorFactory.java
    |   |-- TransferActuator.java
    |   |-- VMActuator.java
    |   |-- ......
    |-- utils
    |-- vm
```

**`actuator` Module Core Structure**

  * `actuator/`: Defines the executors for various types of transactions in the TRON network, with each transaction type corresponding to a specific executor. For example:
      * `TransferActuator`: Handles TRX transfer transactions.
      * `FreezeBalanceV2Actuator`: Handles transactions for staking TRX to obtain resources (Bandwidth or Energy).
  * `utils/`: Encapsulates helper utility classes for the transaction execution process.
  * `vm/`: Contains logic related to the virtual machine.

**Actuator Interface Definition**

The `actuator` module standardizes the transaction execution logic by defining a unified Actuator interface. This interface includes the following core methods:

  * `execute()`: Executes the specific operations of a transaction, such as state changes and business logic processing.
  * `validate()`: Validates the legality of a transaction to prevent invalid or malicious transactions.
  * `getOwnerAddress()`: Gets the address of the transaction originator.
  * `calcFee()`: Calculates the transaction fee required.

Developers can also define and handle custom transaction types by implementing the `Actuator` interface according to their own business needs.

## `crypto` Module

`crypto` is a relatively independent but crucial module in `java-tron`, responsible for the encryption and data security of the entire system. The currently supported cryptographic algorithms include `SM2` and `ECKey`.

The source code for the `crypto` module is located in the [crypto directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/crypto). Its core directory structure is as follows:

```
|-- crypto/src/main/java/org/tron/common/crypto
    |-- Blake2bfMessageDigest.java
    |-- ECKey.java
    |-- Hash.java
    |-- SignInterface.java
    |-- SignUtils.java
    |-- SignatureInterface.java
    |-- cryptohash
    |-- jce
    |-- sm2
```

  * `sm2` and `jce`: Implement the SM2 and ECKey encryption and signature algorithms, respectively, which are widely used in core security scenarios like transaction signing and identity verification.

This module provides the security foundation for the entire TRON network, ensuring the integrity, non-repudiation, and privacy of transaction data, and is a vital pillar supporting on-chain trust.

## `framework` Module

`framework` is the core module of `java-tron` and the entry point for starting a node. It is responsible for initializing the various sub-modules, dispatching business logic, and providing a unified access point for external services, covering core functions such as node network communication, block broadcasting, synchronization, and management.

The source code for the `framework` module is located in the [framework directory of the java-tron repository](https://github.com/tronprotocol/java-tron/tree/develop/framework). Its core directory structure is as follows:

```
|-- framework/src/main/java/org/tron
    |-- common
    |   |-- application
    |   |-- backup
    |   |-- logsfilter
    |   |-- net
    |   |-- overlay
    |   |   |-- client
    |   |   |-- discover
    |   |   |-- message
    |   |   |-- server
    |   |-- runtime
    |-- core
    |   |-- Wallet.java
    |   |-- capsule
    |   |-- config
    |   |-- consensus
    |   |-- db
    |   |-- metrics
    |   |-- net
    |   |-- services
    |   |-- trie
    |   |-- zen
    |-- keystore
    |-- program
    |   |-- FullNode.java
    |-- tool
```

  * `program/FullNode.java`: The program entry point for `java-tron`, responsible for initializing various system components and external interface services (HTTP, gRPC, JSON-RPC, etc.) to support external systems connecting to the TRON network.
  * `core/services`: A unified exit point for external services.
      * `http/`: Defines the control logic for all HTTP interfaces.
      * `json-rpc/`: Implements the JSON-RPC interface, compatible with Ethereum's RPC standard, supporting lightweight access to node functions.
  * `common/overlay/discover`: Implements a node discovery protocol based on Kademlia for discovering and connecting to other nodes on the TRON network.
  * `common/overlay/server`: Manages connected nodes and handles logic for block synchronization, transaction propagation, etc., ensuring block consistency and efficient message passing between nodes.
  * `core/net`: Handles network messages. Its subdirectory `/service` contains the logic for broadcasting transactions and blocks, as well as block fetching and synchronization.
  * `core/db/Manager.java`: The core dispatching class for data processing, responsible for operations like transaction and block validation, application, and persistence. It is the key hub for on-chain data processing.