# Smart Contracts

## Overview

A smart contract is a computational protocol that automates the execution of contractual terms. It defines the conditions and penalties for participants, much like a traditional contract. Once triggered, it self-executes according to the predefined terms and automatically verifies compliance with its coded logic.

TRON is fully compatible with the Ethereum smart contract ecosystem and supports contracts written in the Solidity language. The development workflow is as follows:

1.  Write and compile a Solidity contract in a local or online IDE.
2.  Deploy the contract to the TRON Mainnet.
3.  Once deployed, the contract will be automatically executed on all nodes across the TRON network whenever it is triggered.

You can find the latest version in the [TRON Solidity repository](https://github.com/tronprotocol/solidity/releases).

## TRON Smart Contract Features

The TRON Virtual Machine (TVM) is based on the Ethereum Solidity language. While it is compatible with the features of the Ethereum Virtual Machine (EVM), there are some differences that align with TRON's unique characteristics.

### Smart Contract Definition

Smart contracts running on the TVM are compatible with Ethereum's contract features. The TRON protocol uses **Protocol Buffers** to encapsulate and describe a smart contract, with its data structure defined as follows:

```
message SmartContract {
  message ABI {
    message Entry {
      enum EntryType {
        UnknownEntryType = 0;
        Constructor = 1;
        Function = 2;
        Event = 3;
        Fallback = 4;
        Receive = 5;
        Error = 6;
      }
      message Param {
        bool indexed = 1;
        string name = 2;
        string type = 3;
      }
      enum StateMutabilityType {
        UnknownMutabilityType = 0;
        Pure = 1;
        View = 2;
        Nonpayable = 3;
        Payable = 4;
      }

      bool anonymous = 1;
      bool constant = 2;
      string name = 3;
      repeated Param inputs = 4;
      repeated Param outputs = 5;
      EntryType type = 6;
      bool payable = 7;
      StateMutabilityType stateMutability = 8;
    }
    repeated Entry entrys = 1;
  }
  bytes origin_address = 1;
  bytes contract_address = 2;
  ABI abi = 3;
  bytes bytecode = 4;
  int64 call_value = 5;
  int64 consume_user_resource_percent = 6;
  string name = 7;
  int64 origin_energy_limit = 8;
  bytes code_hash = 9;
  bytes trx_hash = 10;
}
```

**Field Descriptions:**

  - `origin_address`: The address of the contract creator.
  - `contract_address`: The address of the contract.
  - `abi`: The interface information for all functions within the contract.
  - `bytecode`: The contract's bytecode.
  - `call_value`: The amount of TRX (in sun) passed when calling the contract.
  - `consume_user_resource_percent`: The percentage of resource consumption that the caller is responsible for, as set by the developer.
  - `name`: The name of the contract.
  - `origin_energy_limit`: The maximum Energy that the deployer will provide for a single transaction, as set by the developer. This value must be greater than 0. For older contracts deployed without this parameter, `origin_energy_limit` is stored as `0`, but the system still processes them with an Energy limit of 10 million. Developers can later set this value explicitly by calling the `updateEnergyLimit` interface, and the new value must be greater than 0.

Developers can create and trigger smart contracts using the `CreateSmartContract` and `TriggerSmartContract` gRPC message types.

### Using Contract Functions

#### Constant and Non-Constant Functions

Contract functions can be categorized into two types based on whether they modify the on-chain state:

  - **Constant Functions**: Functions decorated with `view`, `pure`, or `constant`. These calls are executed locally on the node and return a result directly without broadcasting a transaction.
  - **Non-Constant Functions**: Functions that modify the on-chain state, such as performing a transfer or changing a contract's internal variables. These calls must be executed by submitting a transaction, which is then confirmed by network consensus.

> **Note**: If the `CREATE` instruction (for dynamically creating contracts) is used within a function, that function will be treated as non-constant and processed as a transaction, even if it is decorated with keywords like `view` or `pure`.

#### Message Calls

During contract execution, you can interact with other contracts or transfer TRX to any account (contract or non-contract) through message calls. Each message call includes attributes such as the sender, recipient, data, transfer amount, fees, and a return value. Message calls can also recursively generate new message calls.

When a contract initiates an internal message call, it can flexibly control the Energy allocation:

  * Specify a maximum Energy limit for the call.
  * Reserve a portion of Energy for the subsequent execution of the current contract.

Typically, the Energy limit for an internal call is set using the pattern `{gas: gasleft() - reserved_energy}`.

If an exception occurs during the call (e.g., `OutOfEnergyException`):

  * The call will return `false` but will not throw an exception.
  * If an Energy limit was set for the call, it will consume at most the Energy allocated to it. If no limit was explicitly set, the call will consume all remaining Energy available to the executing contract.

#### Delegate Call / Code Call and Libraries (`delegatecall`/`callcode`/Library)

A `delegatecall` is a special type of message call. The key difference from a standard message call is that the code at the target address is executed in the **context of the calling contract**, and `msg.sender` and `msg.value` remain unchanged. This allows a contract to dynamically load code from an external address at runtime while ensuring its own storage, address, and balance point to the calling contract; only the code is fetched from the called address.

This mechanism enables Solidity to implement **Libraries**. Developers can deploy reusable code as separate library contracts and then execute this code within the context of calling contracts via `delegatecall`. A typical application is using libraries to implement complex data structures (like linked lists or sets), allowing multiple main contracts to share the same functional logic while avoiding code redundancy.

#### `CREATE` Instruction

The `CREATE` instruction is used to dynamically create new contracts and generate new addresses by an existing contract. Unlike Ethereum, the TVM generates a new address based on a **hash combination of the current smart contract's transaction ID and an internal call counter (`nonce`)**. Here, `nonce` is defined as the **creation sequence number under the root call**. In a single contract execution, each use of the `CREATE` instruction generates an incrementing number: 1 for the first time, 2 for the second, and so on.

> **Note**: Contracts created via the `CREATE` instruction do not automatically save their ABI. If you need to record the ABI, you should deploy the contract using the `deploycontract` gRPC interface.

#### TVM Built-in Functions

TRON smart contracts include various built-in functions to support common on-chain operations. The most frequent is **transferring funds**, which can occur in different scenarios, such as:

  - Transferring TRX along with a transaction during the `constructor` execution.
  - Transferring funds during the execution of a contract function.
  - Using methods like `transfer`, `send`, `call`, `callcode`, and `delegatecall` to perform transfers.

> **Note**: In TRON smart contracts, if a destination address for a transfer has not yet been activated, it cannot be activated through a smart contract transfer. This behavior differs from both Ethereum's handling and the logic of TRON's system contracts.

In addition to transfers, contracts can perform more complex on-chain operations, including:

  - Voting for Super Representatives
  - Staking TRX
  - Delegating resources

The TVM also maintains compatibility with most of Ethereum's built-in functions, allowing developers to quickly migrate and develop contracts based on their existing experience.

## TRON Address Usage in Solidity

Correctly handling addresses in Solidity is crucial for developing smart contracts on TRON. The core concept to understand is the difference in byte length between TRON and Ethereum addresses, and the internal handling the TRON Virtual Machine (TVM) performs to maintain compatibility with Solidity.

**Core Difference: 20 bytes vs. 21 bytes**

  - **Ethereum Address**: A 20-byte value (40 hexadecimal characters).
  - **TRON Address**: A 21-byte value. It consists of a one-byte address prefix (usually `0x41`) followed by the 20-byte core address.

When handling TRON addresses in Solidity, you must follow these guidelines.

#### Address Conversion

When you need to pass a TRON address into a contract, the recommended practice is to pass it as a `uint256` integer and then cast it to the `address` type inside the contract.

```
/**
 * @dev Converts a TRON address in uint256 format to Solidity's address type.
 * @param tronAddress The TRON address in uint256 format, starting with 0x followed by the HexString.
 * @return address The Solidity address type.
 */
function convertFromTronInt(uint256 tronAddress) public view returns(address) {
    return address(tronAddress);
}
```

This syntax is identical to casting other types to `address` in Ethereum.

#### Address Comparison

When comparing an address to a literal constant in Solidity, you must use the 20-byte format; otherwise, it will result in a compiler error. The TVM automatically handles the `0x41` prefix during execution. For example:

```
function compareAddress(address tronAddress) public view returns (uint256) {
    // Incorrect: Including the 0x41 prefix will cause a compiler error.
    // if (tronAddress == 0x41ca35b7d915458ef540ade6068dfe2f44e8fa733c) { ... }

    // Correct: Use the 20-byte address format.
    if (tronAddress == 0xca35b7d915458ef540ade6068dfe2f44e8fa733c) {
        return 1;
    } else {
        return 0;
    }
}
```

> **Note**: Although the constant in the code is 20 bytes, the TVM can still perform the comparison correctly if a full 21-byte TRON address is passed in for the `tronAddress` parameter from an external source (like `wallet-cli`). The function will still correctly return `1`.

#### Address Assignment

Similar to address comparison, when assigning a literal constant to a variable of type `address`, you must also omit the `0x41` prefix and use the 20-byte format. For example:

```
function assignAddress() public pure {
    // Incorrect: Including the 0x41 prefix will cause a compiler error.
    // address newAddress = 0x41ca35b7d915458ef540ade6068dfe2f44e8fa733c;

    // Correct:
    address newAddress = 0xca35b7d915458ef540ade6068dfe2f44e8fa733c;
    // ... subsequent operations
}
```

> **Notes**:
>
>   - When the `newAddress` variable is used for on-chain operations like transfers, the TVM will automatically prepend the `0x41` prefix to form a valid TRON address.
>   - Base58 formatted addresses like `TLLM21wteSPs4hKjbxgmH1L6poyMjeTbHm` are string addresses used by wallets and clients. They cannot be used directly in Solidity code and must first be decoded into a hexadecimal format (HexString).

## Global Variables and Units

In Solidity smart contracts, a series of global variables can be used to access information about the blockchain, transactions, and calls.

#### Currency Units

Similar to Solidity's support for `ether`, the TVM natively supports two currency units: `trx` and `sun`, with the conversion rate of `1 trx = 1,000,000 sun`. Both units are lowercase and case-sensitive.

  * We recommend using **TronIDE** or **TronBox** for TRON smart contract development, as both tools fully support the `trx` and `sun` units.

#### Block and Transaction-Related Global Variables

The following are commonly used global variables and functions in TRON smart contracts. The behavior of some of these variables differs from Ethereum.

**Block Information**

  - `block.blockhash(uint blockNumber) returns (bytes32)`: Returns the hash of the specified block. Only works for the 256 most recent blocks (not including the current block).
  - `block.coinbase (address)`: The address of the Super Representative that produced the current block.
  - `block.number (uint)`: The current block height (i.e., block number).
  - `block.timestamp (uint)`: The current block's timestamp (in seconds).
  - `now (uint)`: The current block's timestamp, equivalent to `block.timestamp`.

**Call and Transaction Information**

  - `msg.data (bytes)`: The complete calldata.
  - `msg.sender (address)`: The sender of the message (the immediate caller).
  - `msg.sig (bytes4)`: The first 4 bytes of the calldata, which is the function identifier.
  - `msg.value (uint)`: The amount of `sun` sent with the message.
  - `tx.origin (address)`: The original initiator of the transaction.

**Gas and Special Variables**

  - `gasleft() returns (uint256)`: The remaining gas.
  - `block.difficulty (uint)`: The difficulty of the current block. On the TRON network, this value is always 0 and its use is not recommended.
  - `block.gaslimit (uint)`: The gas limit of the current block. This is not supported on the TRON network and is temporarily set to 0.
  - `tx.gasprice (uint)`: The gas price of the transaction. On the TRON network, this value is always 0 and its use is not recommended.
