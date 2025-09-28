# gRPC API

## Overview


This document provides a detailed reference for gRPC) APIs in the TRON blockchain network. These APIs allow developers to interact with the TRON network to perform various functions such as account management, transaction broadcasting, smart contract operations, and resource management.

**Note:** SolidityNode is deprecated. The FullNode now supports all gRPCs of the SolidityNode. New developers should only deploy a FullNode.

**API Definition Reference**: This document outlines the functions of the major APIs. Please refer to [api/api.proto](https://github.com/tronprotocol/protocol/blob/master/api/api.proto) for the complete and authoritative technical definitions.


## Account Management

### Get Account Information

```
rpc GetAccount (Account) returns (Account) {}
```

### Get Account Information by ID

```
rpc GetAccountById (Account) returns (Account) {}
```

### Create Account

```
rpc CreateAccount2 (AccountCreateContract) returns (TransactionExtention) {}
```

### Update Account Name

```
rpc UpdateAccount2 (AccountUpdateContract) returns (TransactionExtention) {}
```

### Set Account ID

```
rpc SetAccountId (SetAccountIdContract) returns (Transaction) {}
```

### Update Account Permission

```
rpc AccountPermissionUpdate (AccountPermissionUpdateContract) returns (TransactionExtention) {}
```


## Transaction Operations

### TRX Transfer

```
rpc CreateTransaction2 (TransferContract) returns (TransactionExtention) {}
```

### Broadcast Transaction

```
rpc BroadcastTransaction (Transaction) returns (Return) {}
```

**Description:**
This gRPC is used to send a signed transaction to a node. After being verified by a Super Representative (SR), the transaction will be broadcast to the entire network.

### Query Transaction Information (by Transaction ID)

```
rpc GetTransactionById (BytesMessage) returns (Transaction) {}
```

### Query Transaction Fee and Block Information (by Transaction ID)

```
rpc GetTransactionInfoById (BytesMessage) returns (TransactionInfo) {}
```

### Query Transaction Information from Pending Pool

```
rpc GetTransactionFromPending (BytesMessage) returns (Transaction) {};
```

### Query Pending Pool Transaction ID List

```
rpc GetTransactionListFromPending (EmptyMessage) returns (TransactionIdList) {};
```

### Query Pending Pool Size

```
rpc GetPendingSize (EmptyMessage) returns (NumberMessage) {};
```

### Query Number of Transactions for a Specific Block

```
rpc GetTransactionCountByBlockNum (NumberMessage) returns (NumberMessage) {};
```

### Query a Transaction's Current Permission Weight

```
rpc GetTransactionSignWeight (Transaction) returns (TransactionSignWeight) {};
```

### Query a Transaction's Permission Approval List

```
rpc GetTransactionApprovedList (Transaction) returns (TransactionApprovedList) {};
```

### Query Transactions Sent from a Specific Address

```
rpc GetTransactionsFromThis2 (AccountPaginated) returns (TransactionListExtention) {}
```

### Query Transactions Received at a Specific Address

```
rpc GetTransactionsToThis2 (AccountPaginated) returns (TransactionListExtention) {}
```


## Token (TRC-10) Operations

### Issue a Token

```
rpc CreateAssetIssue2 (AssetIssueContract) returns (TransactionExtention) {}
```

### Update Token Information

```
rpc UpdateAsset2 (UpdateAssetContract) returns (TransactionExtention) {}
```

**Description:**
A token update can only be initiated by the token issuer to update the:
- Token description
- URL
- Maximum Bandwidth consumption per account
- Total Bandwidth consumption

### Token Transfer

```
rpc TransferAsset2 (TransferAssetContract) returns (TransactionExtention) {}
```

### Participate in Token Issuance

```
rpc ParticipateAssetIssue2 (ParticipateAssetIssueContract) returns (TransactionExtention) {}
```

### Query All Issued Token List

```
rpc GetAssetIssueList (EmptyMessage) returns (AssetIssueList) {}
```

### Query Tokens Issued by a Given Account

```
rpc GetAssetIssueByAccount (Account) returns (AssetIssueList) {}
```

### Query Token Information by Token Name

```
rpc GetAssetIssueByName (BytesMessage) returns (AssetIssueContract) {}
```

### Query Token List by Timestamp

```
rpc GetAssetIssueListByTimestamp (NumberMessage) returns (AssetIssueList){}
```

### Query All Token Lists by Page

```
rpc GetPaginatedAssetIssueList (PaginatedMessage) returns (AssetIssueList) {}
```

### Unfreeze Token

```
rpc UnfreezeAsset2 (UnfreezeAssetContract) returns (TransactionExtention) {}
```

### Query Token by Name

```
rpc GetAssetIssueListByName (BytesMessage) returns (AssetIssueList) {}
```

### Query Token by ID

```
rpc GetAssetIssueById (BytesMessage) returns (AssetIssueContract) {}
```



## Super Representative (SR) & Voting

### Vote for a Super Representative Candidate

```
rpc VoteWitnessAccount2 (VoteWitnessContract) returns (TransactionExtention) {}
```

### Query a Super Representative's Brokerage Percentage

```
rpc GetBrokerageInfo (BytesMessage) returns (NumberMessage) {}
```

### Query Unclaimed Rewards

```
rpc GetRewardInfo (BytesMessage) returns (NumberMessage) {}
```

### Update Brokerage Percentage

```
rpc UpdateBrokerage (UpdateBrokerageContract) returns (TransactionExtention) {}
```

### Apply to Become a Super Representative

```
rpc CreateWitness2 (WitnessCreateContract) returns (TransactionExtention) {}
```

**Description:**
Apply to become a TRON Super Representative candidate.

### Update Super Representative Candidate Information

```
rpc UpdateWitness2 (WitnessUpdateContract) returns (TransactionExtention) {}
```

**Description:** Update the Super Representative's website URL.

### Query All Super Representative Candidates

```
rpc ListWitnesses (EmptyMessage) returns (WitnessList) {}
```

### Block Reward Withdrawal

```
rpc WithdrawBalance2 (WithdrawBalanceContract) returns (TransactionExtention) {}
```

### Create a Proposal

```
rpc ProposalCreate (ProposalCreateContract) returns (TransactionExtention) {}
```

### Vote for or Unvote a Proposal

```
rpc ProposalApprove (ProposalApproveContract) returns (TransactionExtention) {}
```

### Delete a Proposal

```
rpc ProposalDelete (ProposalDeleteContract) returns (TransactionExtention) {}
```



## Resource Management (TRX Staking & Delegation)

### Stake TRX (Old version, deprecated)

This interface is deprecated. Please use `FreezeBalanceV2`.
```
rpc FreezeBalance (FreezeBalanceContract) returns (Transaction) {}
```

### Unstake TRX (Old version, deprecated)

```
rpc UnfreezeBalance (UnfreezeBalanceContract) returns (Transaction) {}
```

### Stake TRX V2

```
rpc FreezeBalanceV2 (FreezeBalanceV2Contract) returns (TransactionExtention) {}
```

### Unstake TRX V2

```
rpc UnfreezeBalanceV2 (UnfreezeBalanceV2Contract) returns (TransactionExtention) {}
```

### Delegate Resources

```
rpc DelegateResource (DelegateResourceContract) returns (TransactionExtention) {}
```

### Undelegate Resources

```
rpc UnDelegateResource (UnDelegateResourceContract) returns (TransactionExtention) {}
```

### Cancel All Unstakes

```
rpc CancelAllUnfreezeV2 (CancelAllUnfreezeV2Contract) returns (TransactionExtention) {}
```

### Get Remaining Unstake Count for an Account

```
rpc GetAvailableUnfreezeCount (GetAvailableUnfreezeCountRequestMessage)
     returns (GetAvailableUnfreezeCountResponseMessage) {};
```

### Get Delegable Resources of a Specific Resource Type for an Address (in sun)

```
rpc GetCanDelegatedMaxSize (CanDelegatedMaxSizeRequestMessage) returns (CanDelegatedMaxSizeResponseMessage) {};
```

### Get Matured Unstake Amount That Can Be Withdrawn at a Specific Time

```
rpc GetCanWithdrawUnfreezeAmount (CanWithdrawUnfreezeAmountRequestMessage)
     returns (CanWithdrawUnfreezeAmountResponseMessage) {};
```

### Withdraw Matured Unstakes

After a user executes the `/wallet/unfreezebalancev2` transaction and waits N days (N being a network parameter), they can call this API to retrieve the funds.
```
rpc WithdrawExpireUnfreeze (WithdrawExpireUnfreezeContract) returns (TransactionExtention) {};
```


## Smart Contract Operations

### Deploy a Smart Contract

```
rpc DeployContract (CreateSmartContract) returns (TransactionExtention) {}
```

### Trigger a Smart Contract

```
rpc TriggerContract (TriggerSmartContract) returns (TransactionExtention) {}
```

### Estimate Energy Consumption

```
rpc EstimateEnergy (TriggerSmartContract) returns (EstimateEnergyMessage) {}
```

### Get Smart Contract

```
rpc GetContract (BytesMessage) returns (SmartContract) {}
```

### Update `consume_user_resource_percent` in a Smart Contract

```
rpc UpdateSetting (UpdateSettingContract) returns (TransactionExtention) {}
```

### Update `origin_energy_limit` in a Smart Contract

```
rpc UpdateEnergyLimit (UpdateEnergyLimitContract) returns (TransactionExtention) {}
```


## Market Transactions (Market Order)

### Create a Market Sell Order

```
rpc MarketSellAsset (MarketSellAssetContract) returns (TransactionExtention) {};
```

### Cancel a Market Order

```
rpc MarketCancelOrder (MarketCancelOrderContract) returns (TransactionExtention) {};
```

### Get All Market Orders for an Account

```
rpc GetMarketOrderByAccount (BytesMessage) returns (MarketOrderList) {};
```

### Get All Market Trading Pairs

```
rpc GetMarketPairList (EmptyMessage) returns (MarketOrderPairList) {};
```

### Get All Market Orders for a Trading Pair

```
rpc GetMarketOrderListByPair (MarketOrderPair) returns (MarketOrderList) {};
```

### Get All Market Prices for a Trading Pair

```
rpc GetMarketPriceByPair (MarketOrderPair) returns (MarketPriceList) {};
```

### Get a Market Order by ID

```
rpc GetMarketOrderById (BytesMessage) returns (MarketOrder) {};
```

### Create a Trading Pair

```
rpc ExchangeCreate (ExchangeCreateContract) returns (TransactionExtention) {};
```

### Inject Funds into a Trading Pair

```
rpc ExchangeInject (ExchangeInjectContract) returns (TransactionExtention) {};
```

### Withdraw Funds from a Trading Pair

```
rpc ExchangeWithdraw (ExchangeWithdrawContract) returns (TransactionExtention) {};
```

### Perform a Trade in a Trading Pair

```
rpc ExchangeTransaction (ExchangeTransactionContract) returns (TransactionExtention) {};
```

### Query All Trading Pairs

```
rpc ListExchanges (EmptyMessage) returns (ExchangeList) {}
```

### Query Trading Pairs by Page

```
rpc GetPaginatedExchangeList (PaginatedMessage) returns (ExchangeList) {}
```

### Query Trading Pair by ID

```
rpc GetExchangeById (BytesMessage) returns (Exchange) {}
```


## Blockchain Data Query

### Get Current Block Information

```
rpc GetNowBlock2 (EmptyMessage) returns (BlockExtention) {}
```

### Get Block by Block Number

```
rpc GetBlockByNum2 (NumberMessage) returns (BlockExtention) {}
```

### Get Block Information (by Block ID)

```
rpc GetBlockById (BytesMessage) returns (Block) {}
```

### Get Total Transaction Count (Deprecated, returns 0)

```
rpc TotalTransaction (EmptyMessage) returns (NumberMessage) {}
```

### Query Account Balance at a Specific Block Height

```
rpc GetAccountBalance (AccountBalanceRequest) returns (AccountBalanceResponse){};
```

### Get Account Bandwidth

```
rpc GetAccountNet (Account) returns (AccountNetMessage){};
```

### Get Account Resources (Energy, Bandwidth)

```
rpc GetAccountResource (Account) returns (AccountResourceMessage){};
```
Note: To query historical account balances, a node must have `storage.balance.history.lookup = true` set in its configuration file. You can find official nodes that support this function [here](../using_javatron/backup_restore.md/#fullnode).

### Get Account Balance Changes within a Block

```
rpc GetBlockBalanceTrace (BlockBalanceTrace.BlockIdentifier) returns (BlockBalanceTrace) {};
```

### Get Total Burned TRX Amount

```
rpc GetBurnTrx (EmptyMessage) returns (NumberMessage) {};
```

### Get All Transaction Receipt Information for a Specific Block

```
rpc GetTransactionInfoByBlockNum (NumberMessage) returns (TransactionInfoList) {};
```

### Get Information for a Specific Block

By default, it returns the latest block header. You can also query a specific block header or block information, including the transaction body.
```
rpc GetBlock (BlockReq) returns (BlockExtention) {};
```


## Governance

### Query All Proposals

```
rpc ListProposals (EmptyMessage) returns (ProposalList) {}
```

### Query Proposals by Page

```
rpc GetPaginatedProposalList (PaginatedMessage) returns (ProposalList) {}
```

### Query Proposal by ID

```
rpc GetProposalById (BytesMessage) returns (Proposal) {}
```

### Query All Parameters Settable by the Committee

```
rpc GetChainParameters (EmptyMessage) returns (ChainParameters) {}
```


## Other Types

### Query Next Maintenance Time

```
rpc GetNextMaintenanceTime (EmptyMessage) returns (NumberMessage) {}
```

### Query Node Information

```
rpc GetNodeInfo (EmptyMessage) returns (NodeInfo) {}
```

### Get Historical Change Records for Bandwidth Unit Price

```
rpc GetBandwidthPrices (EmptyMessage) returns (PricesResponseMessage) {}
```

### Get Historical Change Records for Energy Unit Price

```
rpc GetEnergyPrices (EmptyMessage) returns (PricesResponseMessage) {}
```

### Get Historical Change Records for Transaction Memo Fee

```
rpc GetMemoFee (EmptyMessage) returns (PricesResponseMessage) {}
```

### Get Block Reference

```
rpc getBlockReference (EmptyMessage) returns (BlockReference) {}
```

### Get Dynamic Network Parameters

```
rpc GetDynamicProperties (EmptyMessage) returns (DynamicProperties) {}
```

### Get Node Status Information

```
rpc GetStatsInfo (EmptyMessage) returns (MetricsInfo) {}
```

### Get Peer Information

```
rpc ListNodes (EmptyMessage) returns (NodeList) {}
```

### Query Block Information for a Specific Range

```
rpc GetBlockByLimitNext2 (BlockLimit) returns (BlockListExtention) {}
```
