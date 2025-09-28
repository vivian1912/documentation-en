# JSON-RPC API

## Overview
JSON-RPC is a stateless, lightweight remote procedure call (RPC) protocol. The TRON network provides a set of JSON-RPC APIs that are compatible with Ethereum.

Although the APIs are designed for high compatibility with Ethereum, some endpoints may behave differently due to TRON's unique account model, resource model, and consensus mechanism. Additionally, TRON has extended the API set with custom interfaces to support its unique transaction types.

## How to enable or disable JSON-RPC service of a node
By default, the JSON-RPC service in a java-tron node is disabled. You must explicitly enable it in the node's [configuration file](https://github.com/tronprotocol/java-tron/blob/develop/framework/src/main/resources/config.conf).
```
node.jsonrpc {  
    httpFullNodeEnable = true  
    httpFullNodePort = 8545  
    httpSolidityEnable = true  
    httpSolidityPort = 8555  
}
```

## HEX value encoding
In JSON-RPC interactions, all binary data is passed as hexadecimal strings, which follow two distinct formatting rules:

**QUANTITIES (Numerical Types)**
   - Description: Used to represent integers, such as block numbers, balances, and counts.
   - Format: A hexadecimal string with a `0x` prefix, using the most compact representation (i.e., with no leading zeros). The only exception is zero itself, which must be represented as `0x0`.
   - Examples:
      - `0x41` (65 in decimal)
      - `0x400` (1024 in decimal)
      - Incorrect: `0x0400` (leading zeros are not allowed)
      - Incorrect: `ff` (must have a `0x` prefix)

**UNFORMATTED DATA (Byte Arrays)**
   - Description: Used to represent byte arrays, such as addresses, hashes, and bytecode.
   - Format: A hexadecimal string with a `0x` prefix, where each byte is represented by two hex characters.
   - Examples:
      - `0x41` (1-byte data)
      - `0x004200` (3-byte data)
      - `0x` (0-byte data)
      - Incorrect: `0xf0f0f` (must have an even number of digits)
      - Incorrect: `004200` (must have a 0x prefix)

## eth

### eth_accounts
*Returns a list of addresses owned by the client.*

**Parameters:** None
**Return Value:** An empty array.
**Note:** Unlike Ethereum clients such as Geth, TRON nodes do not manage private keys or accounts. Therefore, this interface is provided for compatibility purposes only and does not return any accounts.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '
{"jsonrpc": "2.0", "id": 1, "method": "eth_accounts", "params": []}'

# Returns
{"jsonrpc":"2.0","id":1,"result":[]}
```

### eth_blockNumber
*Returns the number of the most recent block synced by the node.*

**Parameters:** None

**Return Value:** `QUANTITY` - The latest block number.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":64}'

# Returns
{"jsonrpc":"2.0","id":64,"result":"0x20e0cf0"}

```

### eth_call
*Executes a message call transaction locally on the node without broadcasting it to the blockchain. This is primarily used to call view or pure functions in smart contracts or to estimate the outcome of a transaction before sending it.*

**Parameters:**

1. `Object` - The transaction call object, containing the following fields:

    | Field Name | Data Type      | Description                                                   |
    | :-------- | :------------- | :------------------------------------------------------------ |
    | `from`      | DATA, 20 Bytes | The caller's address. Both TRON hex addresses and Ethereum addresses are accepted.    |
    | `to`        | DATA, 20 Bytes | The contract address. |
    | `gas`       | QUANTITY       | Not supported. The value should be `0x0`                               |
    | `gasPrice`  | QUANTITY       | Not supported. The value should be `0x0`                             |
    | `value`     | QUANTITY       | Not supported. The value should be `0x0`                              |
    | `data`      | DATA           | The hash of the method signature and encoded parameters.          |
2. `QUANTITY|TAG` - The block identifier. Currently, only "latest" is currently supported

**Return Value:** `DATA` - The ABI-encoded return value of the executed contract function.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_call",
	"params": [{
		"from": "0xF0CC5A2A84CD0F68ED1667070934542D673ACBD8",
		"to": "0x70082243784DCDF3042034E7B044D6D342A91360",
		"gas": "0x0",
		"gasPrice": "0x0",
		"value": "0x0",
		"data": "0x70a08231000000000000000000000041f0cc5a2a84cd0f68ed1667070934542d673acbd8"
	}, "latest"],
	"id": 1
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x"}
```

### eth_chainId

*Returns the `chainId` of the TRON network, which is derived from the last four bytes of the genesis block hash.*

**Parameters:** None

**Return Value:** `DATA` - The `chainId` of the TRON network.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":79}'

# Returns
{"jsonrpc":"2.0","id":79,"result":"0x2b6653dc"}

```

### eth_coinbase
*Returns the Super Representative address of the current node.*

**Parameters:** None

**Return Value:** `DATA` - The node's Super Representative address. (Note: If multiple SR addresses are configured, it returns the first one. If no valid address is configured or the address has not produced any blocks, it returns an error with the message "etherbase must be explicitly specified".)

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc": "2.0", "id": 1, "method": "eth_coinbase", "params": []}'

# Returns
{"jsonrpc":"2.0","id":1,"error":{"code":-32000,"message":"etherbase must be explicitly specified","data":"{}"}}
```

### eth_estimateGas

*Estimates the Energy required to execute a transaction.*

**Parameters:**
1. `Object` - The transaction call object, containing the following fields:

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `from` | DATA, 20 Bytes | The sender's address. |
| `to` | DATA, 20 Bytes | The receiver's address or contract address. |
| `gas` | QUANTITY | Unused. |
| `gasPrice` | QUANTITY | Unused. |
| `value` | QUANTITY | The amount of TRX sent with the transaction (in sun). |
| `data` | DATA | The hash of the method signature and encoded parameters. |


**Return Value:** `QUANTITY` - The estimated Energy that will be consumed.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"id": 1,
	"method": "eth_estimateGas",
	"params": [{
		"from": "0x41F0CC5A2A84CD0F68ED1667070934542D673ACBD8",
		"to": "0x4170082243784DCDF3042034E7B044D6D342A91360",
		"gas": "0x01",
		"gasPrice": "0x8c",
		"value": "0x01",
		"data": "0x70a08231000000000000000000000041f0cc5a2a84cd0f68ed1667070934542d673acbd8"
	}]
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x0"}
```

### eth_gasPrice

*Returns the current price of Energy on the network (in sun).*

**Parameters:** None

**Return Value:** `QUANTITY` - The current Energy price, in sun.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc": "2.0", "id": 1, "method": "eth_gasPrice", "params": []}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x8c"}
```
### eth_getBalance

*Returns the TRX balance of a specified address.*

**Parameters:**

1. `DATA`, 20 Bytes - The account address to query.
2. `QUANTITY|TAG` - The block identifier. Currently, only "latest" is supported.

**Return Value:** `QUANTITY` - The TRX balance of the address, in sun.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getBalance",
	"params": ["0x41f0cc5a2a84cd0f68ed1667070934542d673acbd8", "latest"],
	"id": 64
}'

# Returns
{"jsonrpc":"2.0","id":64,"result":"0x492780"}
```

### eth_getBlockByHash
*Returns detailed information about a block by its hash.*

**Parameters:**

1. `DATA`, 32 Bytes - The hash of the block.
2. `Boolean` - If `true`, it returns a list of full transaction objects; if `false`, it returns only the transaction hashes.

**Return Value:** `Object` - A block object. Returns null if the block is not found.
The block object contains the following fields:

| Field Name       | Data Type       | Description                                                                                          |
| :--------------- | :-------------- | :--------------------------------------------------------------------------------------------------- |
| `number`         | QUANTITY        | The block number.                                                                                    |
| `hash`           | DATA, 32 Bytes  | The hash of the block.                                                                               |
| `parentHash`     | DATA, 32 Bytes  | The hash of the parent block.                                                                        |
| `nonce`          | QUANTITY        | Unused.                                                                                              |
| `sha3Uncles`     | DATA, 32 Bytes  | Exists for Ethereum JSON-RPC compatibility; has no real meaning.                                     |
| `logsBloom`      | DATA, 256 Bytes | Exists for Ethereum JSON-RPC compatibility; has no real meaning.                                     |
| `transactionsRoot` | DATA, 32 Bytes  | The root of the block's transaction tree.                                                            |
| `stateRoot`      | DATA, 32 Bytes  | Currently has no real meaning.                                                                       |
| `receiptsRoot`   | DATA, 32 Bytes  | Currently has no real meaning.                                                                       |
| `miner`          | DATA, 20 Bytes  | The address of the SR that produced this block.                                                      |
| `difficulty`     | QUANTITY        | Currently has no real meaning.                                                                       |
| `totalDifficulty`| QUANTITY        | Currently has no real meaning.                                                                       |
| `extraData`      | DATA            | Currently has no real meaning.                                                                       |
| `size`           | QUANTITY        | The size of the block in bytes.                                                                      |
| `gasLimit`       | QUANTITY        | The maximum gas allowed in this block.                                                               |
| `gasUsed`        | QUANTITY        | The total gas used by all transactions in this block.                                                |
| `timestamp`      | QUANTITY        | The Unix timestamp of the block's creation, in seconds.                                              |
| `transactions`   | Array           | An array of transaction objects or 32-byte transaction hashes, depending on the second parameter.    |
| `uncles`         | Array           | Currently has no real meaning.                                                                       |


**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getBlockByHash",
	"params": ["0x00000000035dc7288bbde648318b5e42fcd3301ab1a4d12c853910af0ab214d2", false],
	"id": 1
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":null}
```

### eth_getBlockByNumber
*Returns detailed information about a block by its number.*

**Parameters:**

1. `QUANTITY|TAG` - The block number, or the tag "earliest" or "latest".
2. `Boolean` - If `true`, it returns a list of full transaction objects; if `false`, it returns only the transaction hashes.

**Return Value:** `Object` - A block object. Returns null if the block is not found. The structure is the same as in [eth_getBlockByHash](#eth_getblockbyhash).

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getBlockByNumber",
	"params": ["0xF9CC56", true],
	"id": 1
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":null}
```

### eth_getBlockTransactionCountByHash

*Returns the number of transactions in a block by its hash.*

**Parameters:** `DATA`, 32 Bytes - The hash of the block.

**Return Value:** `QUANTITY` - The number of transactions in the block.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"id": 1,
	"method": "eth_getBlockTransactionCountByHash",
	"params": ["0x00000000020ef11c87517739090601aa0a7be1de6faebf35ddb14e7ab7d1cc5b"]
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x39"}
```

### eth_getBlockTransactionCountByNumber

*Returns the number of transactions in a block by its number.*

**Parameters:** `QUANTITY|TAG` - The block number, or the tag "earliest" or "latest".

**Return Value:** `QUANTITY` - The number of transactions in the block.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getBlockTransactionCountByNumber",
	"params": ["0xF96B0F"],
	"id": 1
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x23"}
```

### eth_getCode
*Returns the runtime bytecode of a specified contract address.*

**Parameters:**

1. `DATA`, 20 Bytes - The contract address.
2. `QUANTITY|TAG` - The block identifier. Currently, only "latest" is supported.

**Return Value:** `DATA` - The runtime bytecode. Returns `0x` if the address is not a contract.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getCode",
	"params": ["0x4170082243784DCDF3042034E7B044D6D342A91360", "latest"],
	"id": 64
}'

# Returns
{"jsonrpc":"2.0","id":64,"result":"0x"}
```

### eth_getStorageAt

*Returns the value from a storage position at a given address. This can be used to query the value of variables in a contract.*

**Parameters:**

1. `DATA`, 20 Bytes - The contract address.
2. `QUANTITY` - The index of the storage slot.
3. `QUANTITY|TAG` - The block identifier. Currently, only "latest" is supported.

**Return Value:** `DATA` - The 32-byte value at that storage slot.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getStorageAt",
	"params": ["0xE94EAD5F4CA072A25B2E5500934709F1AEE3C64B", "0x29313b34b1b4beab0d3bad2b8824e9e6317c8625dd4d9e9e0f8f61d7b69d1f26", "latest"],
	"id": 1
}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x0000000000000000000000000000000000000000000000000000000000000000"}
```

### eth_getTransactionByBlockHashAndIndex

*Returns detailed information about a transaction by its block hash and index.*

**Parameters:**

1. `DATA`, 32 Bytes - The hash of the block.
2. `QUANTITY` - The index of the transaction within the block.

**Return Value: **`Object` - A transaction object. Returns `null` if not found.
The transaction object contains the following fields:

| Field Name         | Data Type      | Description                                                                                              |
| :----------------- | :------------- | :------------------------------------------------------------------------------------------------------- |
| `blockHash`        | DATA, 32 Bytes | hash of the block where this transaction was in.                                                         |
| `blockNumber`      | QUANTITY       | block number where this transaction was in.                                                              |
| `from`             | DATA, 20 Bytes | address of the sender                                                                                    |
| `gas`              | QUANTITY       | The Energy consumed by the transaction                                                                   |
| `gasPrice`         | QUANTITY       | The price of Energy.                                                                                     |
| `hash`             | DATA, 32 Bytes | hash of the transaction                                                                                  |
| `input`            | DATA           | the data sent along with the transaction                                                                 |
| `nonce`            | QUANTITY       | unused                                                                                                   |
| `to`               | DATA, 20 Bytes | address of the receiver                                                                                  |
| `transactionIndex` | QUANTITY       | The index of the transaction in the block                                                                |
| `type`             | QUANTITY       | The transaction type. Currently, all transactions on the TRON network are normal transactions, usually with a value of `0x0` |
| `value`            | QUANTITY       | value transferred in sun                                                                                 |
| `v`                | QUANTITY       | ECDSA recovery id                                                                                        |
| `r`                | DATA, 32 Bytes | ECDSA signature r                                                                                        |
| `s`                | DATA, 32 Bytes | ECDSA signature s                                                                                        |

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getTransactionByBlockHashAndIndex",
	"params": ["00000000020ef11c87517739090601aa0a7be1de6faebf35ddb14e7ab7d1cc5b", "0x0"],
	"id": 64
}'

# Returns
{
	"jsonrpc": "2.0",
	"id": 64,
	"result": {
		"blockHash": "0x00000000020ef11c87517739090601aa0a7be1de6faebf35ddb14e7ab7d1cc5b",
		"blockNumber": "0x20ef11c",
		"from": "0xb4f1b6e3a1461266b01c2c4ff9237191d5c3d5ce",
		"gas": "0x0",
		"gasPrice": "0x8c",
		"hash": "0x8dd26d1772231569f022adb42f7d7161dee88b97b4b35eeef6ce73fcd6613bc2",
		"input": "0x",
		"nonce": null,
		"r": "0x6212a53b962345fb8ab02215879a2de05f32e822c54e257498f0b70d33825cc5",
		"s": "0x6e04221f5311cf2b70d3aacfc444e43a5cf14d0bf31d9227218efaabd9b5a812",
		"to": "0x047d4a0a1b7a9d495d6503536e2a49bb5cc72cfe",
		"transactionIndex": "0x0",
		"type": "0x0",
		"v": "0x1b",
		"value": "0x203226"
	}
}
```

### eth_getTransactionByBlockNumberAndIndex

*Returns detailed information about a transaction by its block number and index.*

**Parameters:**

1. `QUANTITY|TAG` - The block number, or the tag "earliest" or "latest".
2. `QUANTITY` - The index of the transaction within the block.

**Return Value:** `Object` - A transaction object. Returns `null` if not found. The structure is the same as in [eth_getTransactionByBlockHashAndIndex](#eth_gettransactionbyblockhashandindex).

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getTransactionByBlockNumberAndIndex",
	"params": ["0xfb82f0", "0x0"],
	"id": 64
}'

# Returns
{"jsonrpc":"2.0","id":64,"result":null}
```

### eth_getTransactionByHash
*Returns detailed information about a transaction by its hash.*

**Parameters:** `DATA`, 32 Bytes - The hash of the transaction.

**Return Value:** `Object` - A transaction object. Returns `null` if not found. The structure is the same as in [eth_getTransactionByBlockHashAndIndex](#eth_gettransactionbyblockhashandindex).

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getTransactionByHash",
	"params": ["c9af231ad59bcd7e8dcf827afd45020a02112704dce74ec5f72cb090aa07eef0"],
	"id": 64
}'

# Returns
{
	"jsonrpc": "2.0",
	"id": 64,
	"result": {
		"blockHash": "0x00000000020ef11c87517739090601aa0a7be1de6faebf35ddb14e7ab7d1cc5b",
		"blockNumber": "0x20ef11c",
		"from": "0x6eced5214d62c3bc9eaa742e2f86d5c516785e14",
		"gas": "0x0",
		"gasPrice": "0x8c",
		"hash": "0xc9af231ad59bcd7e8dcf827afd45020a02112704dce74ec5f72cb090aa07eef0",
		"input": "0x",
		"nonce": null,
		"r": "0x433eaf0a7df3a08c8828a2180987146d39d44de4ac327c4447d0eeda42230ea8",
		"s": "0x6f91f63b37f4d1cd9342f570205beefaa5b5ba18d616fec643107f8c1ae1339d",
		"to": "0x0697250b9d73b460a9d2bbfd8c4cacebb05dd1f1",
		"transactionIndex": "0x6",
		"type": "0x0",
		"v": "0x1b",
		"value": "0x1cb2310"
	}
}
```

### eth_getTransactionReceipt

*Returns the receipt of a transaction by its hash. The receipt contains the execution result, event logs, and resources consumed. This endpoint is comparable to the [wallet/gettransactioninfobyid](http.md#walletgettransactioninfobyid) HTTP API.*

**Parameters:** `DATA`, 32 Bytes - The hash of the transaction.

**Return Value:** `Object` - A transaction receipt object. Returns `null` if the transaction is unconfirmed or not found.

The transaction receipt object contains the following fields:

| Field Name        | Data Type       | Description                                                                               |
| :---------------- | :-------------- | :---------------------------------------------------------------------------------------- |
| `transactionHash`   | DATA, 32 Bytes  | hash of the transaction                                                                   |
| `transactionIndex`  | QUANTITY        | integer of the transaction's index position in the block                                   |
| `blockHash`         | DATA, 32 Bytes  | hash of the block where this transaction was in.                                          |
| `blockNumber`       | QUANTITY        | block number where this transaction was in.                                               |
| `from`              | DATA, 20 Bytes  | address of the sender                                                                     |
| `to`                | DATA, 20 Bytes  | address of the receiver                                                                   |
| `cumulativeGasUsed` | QUANTITY        | The total amount of gas used when this transaction was executed in the block.             |
| `gasUsed`           | QUANTITY        | The amount of gas used by this specific transaction alone.                                |
| `contractAddress`   | DATA, 20 Bytes  | The contract address created, if the transaction was a contract creation, otherwise null. |
| `logs`              | Array           | Array of log objects, which this transaction generated.                                   |
| `logsBloom`         | DATA, 256 Bytes | Bloom filter for light clients to quickly retrieve related logs.                          |
| `root`              | DATA            | 32 bytes of post-transaction stateroot (pre Byzantium)                                    |
| `status`            | QUANTITY        | either 1 (success) or 0 (failure)                                                         |
| `type`              | QUANTITY        | The transaction type. Currently, all transactions on the TRON network are normal transactions with a value of 0. |


**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getTransactionReceipt",
	"params": ["c9af231ad59bcd7e8dcf827afd45020a02112704dce74ec5f72cb090aa07eef0"],
	"id": 64
}'

# Returns
{
	"jsonrpc": "2.0",
	"id": 64,
	"result": {
		"blockHash": "0x00000000020ef11c87517739090601aa0a7be1de6faebf35ddb14e7ab7d1cc5b",
		"blockNumber": "0x20ef11c",
		"contractAddress": null,
		"cumulativeGasUsed": "0x646e2",
		"effectiveGasPrice": "0x8c",
		"from": "0x6eced5214d62c3bc9eaa742e2f86d5c516785e14",
		"gasUsed": "0x0",
		"logs": [],
		"logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		"status": "0x1",
		"to": "0x0697250b9d73b460a9d2bbfd8c4cacebb05dd1f1",
		"transactionHash": "0xc9af231ad59bcd7e8dcf827afd45020a02112704dce74ec5f72cb090aa07eef0",
		"transactionIndex": "0x6",
		"type": "0x0"
	}
}
```

### eth_getWork

*Returns the hash of the current block.*

**Parameters:** None

**Return Value: **`Array` - An array with three elements, where only the first element (the block hash) is relevant.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
	"jsonrpc": "2.0",
	"method": "eth_getWork",
	"params": [],
	"id": 73
}'

# Returns
{
	"jsonrpc": "2.0",
	"id": 73,
	"result": ["0x00000000020e73915413df0c816e327dc4b9d17069887aef1fff0e854f8d9ad0", null, null]
}
```

### eth_protocolVersion

*Returns the TRON protocol version of the node.*

**Parameters:** None

**Return Value:** `String` - The current protocol version number.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_protocolVersion","params":[],"id":64}'

# Returns
{"jsonrpc":"2.0","id":64,"result":"0x16"}
```

### eth_syncing

*Returns the synchronization status of the node.*

**Parameters:** None

**Return Value:** `Object` or `Boolean` - If the node is syncing, it returns an object with `startingBlock`, `currentBlock`, and `highestBlock`. If it is fully synced, it returns `false`.

The fields are described below:


|     Field Name          |   Data Type       |  Description                                                                                           |
| :------------ | :------- | :------------------------------------------------------------------------------------------ |
| `startingBlock` | QUANTITY | The starting block for current synchronization |
| `currentBlock`  | QUANTITY | The current block                                                                          |
| `highestBlock`  | QUANTITY | The estimated highest block                                                                |

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_syncing","params":[],"id":64}'

# Returns
{
    "jsonrpc": "2.0",
	"id": 64,
	"result": {
		"startingBlock": "0x20e76cc",
		"currentBlock": "0x20e76df",
		"highestBlock": "0x20e76e0"
	}
}
```

### eth_newFilter

*Creates a filter to listen for event logs.*

**Parameters:**

1. Object - The filter options object:

| Field     | Type                  | Description                                                               |
| :-------- | :-------------------- | :------------------------------------------------------------------------ |
| `fromBlock` | QUANTITY\|TAG         | Integer block number, or "latest", or "earliest"                                        |
| `toBlock`   | QUANTITY\|TAG         | Integer block number, or "latest", or "earliest"                                   |
| `address`   | DATA\|Array, 20 Bytes | Contract address or a list of addresses from which logs should originate. |
| `topics`    | Array of DATA         |An array of 32-byte DATA topics to filter events. The order is significant. Each topic position can also be an array of DATA, representing an "OR" condition.                                                                 |

**Return Value:** `QUANTITY` - The newly created filter ID.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_newFilter","params":[{"address":["cc2e32f2388f0096fae9b055acffd76d4b3e5532","E518C608A37E2A262050E10BE0C9D03C7A0877F3"],"fromBlock":"0x989680","toBlock":"0x9959d0","topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",null,["0x0000000000000000000000001806c11be0f9b9af9e626a58904f3e5827b67be7","0x0000000000000000000000003c8fb6d064ceffc0f045f7b4aee6b3a4cefb4758"]]}],"id":1}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x2bab51aee6345d2748e0a4a3f4569d80"}
```

### eth_newBlockFilter

*Creates a filter to listen for new blocks.*

**Parameters: **None

**Return Value:** `QUANTITY` - The newly created filter ID.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_newBlockFilter","params":[],"id":1}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x2bab51aee6345d2748e0a4a3f4569d80"}
```

### eth_getFilterChanges

*Polls a filter and returns an array of logs or blocks that have occurred since the last poll.*

**Parameters: **`QUANTITY` - The ID of the filter created by `eth_newFilter` or `eth_newBlockFilter`.

**Return Value:**
 - For filters created with `eth_newFilter`, it returns a list of log objects. Each log object includes:

| Field            | Type           | Description                                                                                 |
| :--------------- | :------------- | :------------------------------------------------------------------------------------------ |
| `removed`          | TAG            | true when the log was removed, due to a chain reorganization. false if its a valid log. |
| `logIndex`         | QUANTITY       | Integer of the log index position in the block. null when its pending log.                  |
| `transactionIndex` | QUANTITY       | Integer of the transactions index position log was created from. null when its pending log. |
| `transactionHash`  | DATA, 32Bytes  | Hash of the transactions this log was created from.                                         |
| `blockHash`        | DATA, 32 Bytes | Hash of the block where this log was in. null when its pending.                             |
| `blockNumber`      | QUANTITY       | The block number where this log was in.                                                     |
| `address`          | DATA, 32 Bytes | Address from which this log originated.                                                     |
| `data`             | DATA           | Contains one or more 32 Bytes non-indexed arguments of the log.                             |
| `topics`           | DATA[]         | Event topic and indexed arguments.                                                          |

 - For filters created with `eth_newBlockFilter`, it returns a list of block hashes.


**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
    "jsonrpc": "2.0",
    "method": "eth_getFilterChanges",
    "params": [     "0xc11a84d5e906ecb9f5c1eb65ee940b154ad37dce8f5ac29c80764508b901d996"
    ],
    "id": 71
}'

# Returns
{
    "jsonrpc": "2.0",
    "id": 71,
    "error": {
        "code": -32000,
        "message": "filter not found",
        "data": "{}"
    }
}
```

### eth_getFilterLogs

*Returns an array of all logs matching a given filter ID.*

**Parameters:** `QUANTITY` - The ID of the filter created by `eth_newFilter`.

**Return Value:** `Array` - An array of log objects. See `eth_getFilterChanges` for the structure.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
    "jsonrpc": "2.0",
    "method": "eth_getFilterLogs",
    "params": [      "0xc11a84d5e906ecb9f5c1eb65ee940b154ad37dce8f5ac29c80764508b901d996"
    ],
    "id": 71
}'

# Returns
{
    "jsonrpc": "2.0",
    "id": 71,
    "error": {
        "code": -32000,
        "message": "filter not found",
        "data": "{}"
    }
}
```

### eth_uninstallFilter

*Uninstalls a filter with the given ID. This should always be called when you are done watching. Also, filters time out if they are not requested with `eth_getFilterChanges` for a period of time.*

**Parameters:** `QUANTITY` - The ID of the filter to uninstall.

**Return Value:** `Boolean` - `true` if the filter was successfully uninstalled, `false` otherwise.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
    "jsonrpc": "2.0",
    "method": "eth_uninstallFilter",
    "params": [     "0xc11a84d5e906ecb9f5c1eb65ee940b154ad37dce8f5ac29c80764508b901d996"
 ],
    "id": 71
}'

# Returns
{
    "jsonrpc": "2.0",
    "id": 71,
    "result": true
}
```

### eth_getLogs
*Returns an array of all logs matching a given filter object.*

**Parameters:** Object - The filter options object, same as eth_newFilter, but can additionally include a blockhash field to query a specific block.

| Field     | Type                  | Description                                                                                                                      |
| :-------- | :-------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `fromBlock` | QUANTITY\|TAG         | (optional, default: "latest") Integer block number, or "latest" for the latest block                                        |
| `toBlock`   | QUANTITY\|TAG         | (optional, default: "latest") Integer block number, or "latest" for the latest block                                          |
| `address`   | DATA\|Array, 20 Bytes | (optional) Contract address or a list of addresses from which logs should originate.                       |
| `topics`    | Array of DATA         | (optional) Array of 32 Bytes DATA topics. Topics are order-dependent. Each topic can also be an array of DATA with "or" options. |
| `blockhash` | DATA, 32 Bytes        | (Optional) The block hash. Note: `blockHash` and `fromBlock/toBlock` cannot be specified at the same time, or it will result in an error: `"cannot specify both BlockHash and FromBlock/ToBlock, choose one or the other"`.                                                                                                         |

**Return Value:** `Array` - An array of log objects. See [eth_getFilterChanges](#eth_getfilterchanges) for the structure.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"eth_getLogs","params":[{"address":["cc2e32f2388f0096fae9b055acffd76d4b3e5532","E518C608A37E2A262050E10BE0C9D03C7A0877F3"],"fromBlock":"0x989680","toBlock":"0x9959d0","topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",null,["0x0000000000000000000000001806c11be0f9b9af9e626a58904f3e5827b67be7","0x0000000000000000000000003c8fb6d064ceffc0f045f7b4aee6b3a4cefb4758"]]}],"id":1}'

# Returns
{
    "jsonrpc": "2.0",
    "id": 71,
    "result": []
}
```

## net

### net_listening
*Returns `true` if the client is actively listening for network connections.*

**Parameters:** None
**Return Value:** `Boolean` - `true` if listening, `false` otherwise.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"net_listening","params":[],"id":64}'

# Returns
{"jsonrpc":"2.0","id":64,"result":true}
```

### net_peerCount

**Returns the number of peers currently connected to the client.**

**Parameters:** None

**Return Value:** `QUANTITY` - The integer number of connected peers.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"net_peerCount","params":[],"id":64}'

# Returns
{"jsonrpc":"2.0","id":64,"result":"0x9"}
```

### net_version

*Returns the genesis block hash.*

**Parameters:** None
**Return Value:** `String` - The network ID (Chain ID).

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":64}'

# Returns
{"jsonrpc":"2.0","id":64,"result":"0x2b6653dc"}
```

## web3

### web3_clientVersion
*Returns the current client version.*

**Parameters:** None

**Return Value:** String - The client version.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc": "2.0", "id": 1, "method": "web3_clientVersion", "params": []}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"TRON/v4.8.0/Linux/Java1.8"}
```

### web3_sha3
*Returns the Keccak-256 hash (not the standardized SHA3-256) of the given data.*

**Parameters:** `DATA` - The data to be hashed.
**Return Value:** `DATA` - The 32-byte Keccak-256 hash result.

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"jsonrpc": "2.0", "id": 1, "method": "web3_sha3", "params": ["0x68656c6c6f20776f726c64"]}'

# Returns
{"jsonrpc":"2.0","id":1,"result":"0x47173285a8d7341e5e972fc677286384f802f8ef42a5ec5f03bbfa254cb01fad"}
```

## buildTransaction
*This is a TRON-specific RPC method used to conveniently create native TRON transactions. It returns an unsigned transaction object. Different transaction types have different parameters.*

### TransferContract (TRX Transfer)
**Parameters:** 

`Object` - with the following fields:
| Param Name | Type      | Description                                |
| :--------- | :------------- | :------------------------------------------ |
| `from`       | DATA, 20 Bytes | The address the transaction is sent from.   |
| `to`         | DATA, 20 Bytes | The address the transaction is directed to.|
| `value`      | DATA           |  the transfer amount                        |

**Return Value:** 
`Object` - An object containing the unsigned TransferContract transaction.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
    "id": 1337,
    "jsonrpc": "2.0",
    "method": "buildTransaction",
    "params": [
        {
            "from": "0xC4DB2C9DFBCB6AA344793F1DDA7BD656598A06D8",
            "to": "0x95FD23D3D2221CFEF64167938DE5E62074719E54",
            "value": "0x1f4"
        }]}'

# Returns
{"jsonrpc":"2.0","id":1337,"result":{"transaction":{"visible":false,"txID":"ae02a80abd985a6f05478b9bbf04706f00cdbf71e38c77d21ed77e44c634cef9","raw_data":{"contract":[{"parameter":{"value":{"amount":500,"owner_address":"41c4db2c9dfbcb6aa344793f1dda7bd656598a06d8","to_address":"4195fd23d3d2221cfef64167938de5e62074719e54"},"type_url":"type.googleapis.com/protocol.TransferContract"},"type":"TransferContract"}],"ref_block_bytes":"957e","ref_block_hash":"3922d8c0d28b5283","expiration":1684469286000,"timestamp":1684469226841},"raw_data_hex":"0a02957e22083922d8c0d28b528340f088c69183315a66080112620a2d747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e5472616e73666572436f6e747261637412310a1541c4db2c9dfbcb6aa344793f1dda7bd656598a06d812154195fd23d3d2221cfef64167938de5e62074719e5418f40370d9bac2918331"}}}

```

### TransferAssetContract (TRC-10 Transfer)
**Parameters:** 
`Object` - with the following fields:

| Param Name | Type      | Description                                |
| :--------- | :------------- | :----------------------------------------- |
| `from`       | DATA, 20 Bytes | The address the transaction is sent from  |
| `to`         | DATA, 20 Bytes | The address the transaction is directed to |
| `tokenId`    | QUANTITY       | Token ID                                   |
| `tokenValue` | QUANTITY       | The transfer amount of TRC-10               |

**Return Value:** 
`Object` - An object containing the unsigned `TransferAssetContract` transaction.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
    "method": "buildTransaction",
    "params": [
        {
            "from": "0xC4DB2C9DFBCB6AA344793F1DDA7BD656598A06D8",
            "to": "0x95FD23D3D2221CFEF64167938DE5E62074719E54",
            "tokenId": 1000016,
            "tokenValue": 20
        }
    ],
    "id": 44,
    "jsonrpc": "2.0"
}

# Returns
{"jsonrpc":"2.0","id":44,"error":{"code":-32600,"message":"assetBalance must be greater than 0.","data":"{}"}}
```
### CreateSmartContract (Deploy Contract)

**Parameters:** 
`Object` - with the following fields:

| Param Name                 | Type          | Description                                   |
| :------------------------- | :------------ | :-------------------------------------------- |
| `from`                     | DATA, Bytes   | The address the transaction is sent from      |
| `name`                     | DATA          | The name of the smart contract                |
| `gas`                      | DATA          | Fee limit                                     |
| `abi`                      | DATA          | The ABI of the smart contract                 |
| `data`                     | DATA          | The byte code of the smart contract           |
| `consumeUserResourcePercent` | QUANTITY      | The consume user resource percent             |
| `originEnergyLimit`        | QUANTITY      | The origin Energy limit                       |
| `value`                    | DATA          | The Amount of TRX transferred to the contract |
| `tokenId`                  | QUANTITY      | Token ID                                      |
| `tokenValue`               | QUANTITY      | The transfer amount of TRC-10                  |


**Returns**

`Object` - transaction of `CreateSmartContract` or an error

**Example**
```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{
    "id": 1337,
    "jsonrpc": "2.0",
    "method": "buildTransaction",
    "params": [
        {
            "from": "0xC4DB2C9DFBCB6AA344793F1DDA7BD656598A06D8",
            "name": "transferTokenContract",
            "gas": "0x245498",
            "abi": "[{\"constant\":false,\"inputs\":[],\"name\":\"getResultInCon\",\"outputs\":[{\"name\":\"\",\"type\":\"trcToken\"},{\"name\":\"\",\"type\":\"uint256\"},{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":true,\"stateMutability\":\"payable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"toAddress\",\"type\":\"address\"},{\"name\":\"id\",\"type\":\"trcToken\"},{\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"TransferTokenTo\",\"outputs\":[],\"payable\":true,\"stateMutability\":\"payable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[],\"name\":\"msgTokenValueAndTokenIdTest\",\"outputs\":[{\"name\":\"\",\"type\":\"trcToken\"},{\"name\":\"\",\"type\":\"uint256\"},{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":true,\"stateMutability\":\"payable\",\"type\":\"function\"},{\"inputs\":[],\"payable\":true,\"stateMutability\":\"payable\",\"type\":\"constructor\"}]\n",
            "data": "6080604052d3600055d2600155346002556101418061001f6000396000f3006080604052600436106100565763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166305c24200811461005b5780633be9ece71461008157806371dc08ce146100aa575b600080fd5b6100636100b2565b60408051938452602084019290925282820152519081900360600190f35b6100a873ffffffffffffffffffffffffffffffffffffffff600435166024356044356100c0565b005b61006361010d565b600054600154600254909192565b60405173ffffffffffffffffffffffffffffffffffffffff84169082156108fc029083908590600081818185878a8ad0945050505050158015610107573d6000803e3d6000fd5b50505050565bd3d2349091925600a165627a7a72305820a2fb39541e90eda9a2f5f9e7905ef98e66e60dd4b38e00b05de418da3154e7570029",
            "consumeUserResourcePercent": 100,
            "originEnergyLimit": 11111111111111,
            "value": "0x1f4",
            "tokenId": 1000033,
            "tokenValue": 100000
        }
    ]
}

# Returns
{"jsonrpc":"2.0","id":1337,"result":{"transaction":{"visible":false,"txID":"598d8aafbf9340e92c8f72a38389ce9661b643ff37dd2a609f393336a76025b9","contract_address":"41dfd93697c0a978db343fe7a92333e11eeb2f967d","raw_data":{"contract":[{"parameter":{"value":{"token_id":1000033,"owner_address":"41c4db2c9dfbcb6aa344793f1dda7bd656598a06d8","call_token_value":100000,"new_contract":{"bytecode":"6080604052d3600055d2600155346002556101418061001f6000396000f3006080604052600436106100565763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166305c24200811461005b5780633be9ece71461008157806371dc08ce146100aa575b600080fd5b6100636100b2565b60408051938452602084019290925282820152519081900360600190f35b6100a873ffffffffffffffffffffffffffffffffffffffff600435166024356044356100c0565b005b61006361010d565b600054600154600254909192565b60405173ffffffffffffffffffffffffffffffffffffffff84169082156108fc029083908590600081818185878a8ad0945050505050158015610107573d6000803e3d6000fd5b50505050565bd3d2349091925600a165627a7a72305820a2fb39541e90eda9a2f5f9e7905ef98e66e60dd4b38e00b05de418da3154e7570029","consume_user_resource_percent":100,"name":"transferTokenContract","origin_address":"41c4db2c9dfbcb6aa344793f1dda7bd656598a06d8","abi":{"entrys":[{"outputs":[{"type":"trcToken"},{"type":"uint256"},{"type":"uint256"}],"payable":true,"name":"getResultInCon","stateMutability":"Payable","type":"Function"},{"payable":true,"inputs":[{"name":"toAddress","type":"address"},{"name":"id","type":"trcToken"},{"name":"amount","type":"uint256"}],"name":"TransferTokenTo","stateMutability":"Payable","type":"Function"},{"outputs":[{"type":"trcToken"},{"type":"uint256"},{"type":"uint256"}],"payable":true,"name":"msgTokenValueAndTokenIdTest","stateMutability":"Payable","type":"Function"},{"payable":true,"stateMutability":"Payable","type":"Constructor"}]},"origin_energy_limit":11111111111111,"call_value":500}},"type_url":"type.googleapis.com/protocol.CreateSmartContract"},"type":"CreateSmartContract"}],"ref_block_bytes":"80be","ref_block_hash":"ac7c3d59c55ac92c","expiration":1634030190000,"fee_limit":333333280,"timestamp":1634030131693},"raw_data_hex":"0a0280be2208ac7c3d59c55ac92c40b0fba79ec72f5ad805081e12d3050a30747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e437265617465536d617274436f6e7472616374129e050a1541c4db2c9dfbcb6aa344793f1dda7bd656598a06d812fc040a1541c4db2c9dfbcb6aa344793f1dda7bd656598a06d81adb010a381a0e676574526573756c74496e436f6e2a0a1a08747263546f6b656e2a091a0775696e743235362a091a0775696e743235363002380140040a501a0f5472616e73666572546f6b656e546f22141209746f416464726573731a0761646472657373220e120269641a08747263546f6b656e22111206616d6f756e741a0775696e743235363002380140040a451a1b6d7367546f6b656e56616c7565416e64546f6b656e4964546573742a0a1a08747263546f6b656e2a091a0775696e743235362a091a0775696e743235363002380140040a0630013801400422e0026080604052d3600055d2600155346002556101418061001f6000396000f3006080604052600436106100565763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166305c24200811461005b5780633be9ece71461008157806371dc08ce146100aa575b600080fd5b6100636100b2565b60408051938452602084019290925282820152519081900360600190f35b6100a873ffffffffffffffffffffffffffffffffffffffff600435166024356044356100c0565b005b61006361010d565b600054600154600254909192565b60405173ffffffffffffffffffffffffffffffffffffffff84169082156108fc029083908590600081818185878a8ad0945050505050158015610107573d6000803e3d6000fd5b50505050565bd3d2349091925600a165627a7a72305820a2fb39541e90eda9a2f5f9e7905ef98e66e60dd4b38e00b05de418da3154e757002928f40330643a157472616e73666572546f6b656e436f6e747261637440c7e3d28eb0c30218a08d0620e1843d70edb3a49ec72f9001a086f99e01"}}}
```


### TriggerSmartContract (Trigger Contract)

**Parameters:** 
`Object` - with the following fields:

| Param Name | Type      | Description                                |
| :------------------------- | :------------- | :--------------------------------------- |
| `from` | DATA, 20 Bytes | The address the transaction is sent from |
| `to` | DATA, 20 Bytes | The address of the smart contract |
| `data` | DATA | The invoked contract function and parameters|
| `gas` | DATA | Fee limit|
| `value` | DATA | The Amount of TRX transferred to the contract |
| `tokenId` | QUANTITY | The token ID. |
| `tokenValue` | QUANTITY | The transfer amount of TRC-10 |

**Return Value:** 
`Object` - `TriggerSmartContract` transaction or an error.

**Example**

```
curl -X POST 'https://api.shasta.trongrid.io/jsonrpc' --data '{"id": 1337,
    "jsonrpc": "2.0",
    "method": "buildTransaction",
    "params": [
        {
            "from": "0xC4DB2C9DFBCB6AA344793F1DDA7BD656598A06D8",
            "to": "0xf859b5c93f789f4bcffbe7cc95a71e28e5e6a5bd",
            "data": "0x3be9ece7000000000000000000000000ba8e28bdb6e49fbb3f5cd82a9f5ce8363587f1f600000000000000000000000000000000000000000000000000000000000f42630000000000000000000000000000000000000000000000000000000000000001",
            "gas": "0x245498",
            "value": "0xA",
            "tokenId": 1000035,
            "tokenValue": 20
        }
    ]
    }
'

# Returns
{"jsonrpc":"2.0","id":1337,"result":{"transaction":{"visible":false,"txID":"c3c746beb86ffc366ec0ff8bf6c9504c88f8714e47bc0009e4f7e2b1d49eb967","raw_data":{"contract":[{"parameter":{"value":{"amount":10,"owner_address":"41c4db2c9dfbcb6aa344793f1dda7bd656598a06d8","to_address":"41f859b5c93f789f4bcffbe7cc95a71e28e5e6a5bd"},"type_url":"type.googleapis.com/protocol.TransferContract"},"type":"TransferContract"}],"ref_block_bytes":"958c","ref_block_hash":"9d8c6bae734a2281","expiration":1684469328000,"timestamp":1684469270364},"raw_data_hex":"0a02958c22089d8c6bae734a22814080d1c89183315a65080112610a2d747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e5472616e73666572436f6e747261637412300a1541c4db2c9dfbcb6aa344793f1dda7bd656598a06d8121541f859b5c93f789f4bcffbe7cc95a71e28e5e6a5bd180a70dc8ec5918331"}}}
```

