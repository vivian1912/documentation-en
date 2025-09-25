# System Contract

The TRON network supports a wide variety of transaction types, such as TRX transfers, TRC-10 token transfers, smart contract deployments and calls, and TRX staking. Each transaction type is defined and executed by a specific system contract. Developers can create these transactions by calling different API endpoints.

For example, deploying a smart contract requires calling the `wallet/deploycontract` endpoint, which corresponds to the `CreateSmartContract` type. Staking TRX for resources requires calling the `wallet/freezebalancev2` endpoint, corresponding to the `FreezeBalanceV2Contract` type.

This document will provide a detailed introduction to the main system contract types on the TRON network and their parameters:

* [**Account Management Contracts**](#account-contracts): Covers the creation and updating of accounts.
* [**TRX Transfer & Resource Contracts**](#trx-resource-contracts): Handles transfers of the native TRX token and the staking and delegation of network resources like Bandwidth and Energy.
* [**TRC-10 Token Contracts**](#trc10-token-contracts): Defines the rules for the issuance, transfer, and management of TRC-10 standard tokens.
* [**Super Representative & Voting Contracts**](#sr-voting-contracts): Covers node election and voting operations within the TRON network's consensus mechanism.
* [**Proposal & Governance Contracts**](#proposal-governance-contracts): For the on-chain governance mechanism used to modify network parameters.
* [**Smart Contract Management Contracts**](#smart-contract-contracts): Supports the deployment, triggering, and configuration of TRC-20 and other smart contracts.
* [**Account Permission Management**](#permission-management): Introduces permission settings for advanced account features, such as multi-signature.


<a id="account-contracts"></a>
## Account Management Contracts

### AccountCreateContract

*Creates a new account.*

```
message AccountCreateContract {
    bytes owner_address = 1;
    bytes account_address = 2;
    AccountType type = 3;
}
```

  * `owner_address`: The address of the contract initiator.
  * `account_address`: The address of the account to be created.
  * `type`: The account type.
      * `0`: Normal account.
      * `1`: An initial account in the genesis block.
      * `2`: Smart contract account.

### AccountUpdateContract

*Updates an account's name.*

```
// Update account name. Account name is unique now.
message AccountUpdateContract {
    bytes account_name = 1;
    bytes owner_address = 2;
}
```

  * `owner_address`: The address of the contract initiator.
  * `account_name`: The account name.

### SetAccountIdContract

*Sets an account's ID.*

```
// Set account id if the account has no id. Account id is unique and case insensitive.
message SetAccountIdContract {
    bytes account_id = 1;
    bytes owner_address = 2;
}
```

  * `owner_address`: The address of the contract initiator.
  * `account_id`: The account ID, which is unique and case-insensitive.


<a id="trx-resource-contracts"></a>
## TRX Transfer & Resource Contracts

### TransferContract

*Transfers TRX.*

```
message TransferContract {
    bytes owner_address = 1;
    bytes to_address = 2;
    int64 amount = 3;
}
```

  * `owner_address`: The address of the contract initiator.
  * `to_address`: The destination account address.
  * `amount`: The transfer amount, in **sun** (1 TRX = 1,000,000 sun).

### FreezeBalanceV2Contract

*Stakes TRX to obtain resources (Stake 2.0).*

```
message FreezeBalanceV2Contract {
    bytes owner_address = 1;
    int64 frozen_balance = 2;
    ResourceCode resource = 3; // Type can be Bandwidth or Energy
}
```

  * `owner_address`: The staker's address.
  * `frozen_balance`: The amount of TRX to stake.
  * `resource`: The type of resource to obtain by staking TRX.

### UnfreezeBalanceV2Contract

*Unstakes TRX (Stake 2.0).*

```
message UnfreezeBalanceV2Contract {
    bytes owner_address = 1;
    int64 unfreeze_balance = 2;
    ResourceCode resource = 3;
}
```

  * `owner_address`: The unstaker's address.
  * `unfreeze_balance`: The amount of TRX to unstake.
  * `resource`: The type of resource to unstake.

### WithdrawExpireUnfreezeContract

*Withdraws the principal of expired unstaked TRX.*

```
message WithdrawExpireUnfreezeContract {
    bytes owner_address = 1;
}
```

  * `owner_address`: The address of the account withdrawing the principal.

### DelegateResourceContract

*Delegates resources.*

```
message DelegateResourceContract {
    bytes owner_address = 1;
    ResourceCode resource = 2;
    int64 balance = 3;
    bytes receiver_address = 4;
    bool  lock = 5;
    int64 lock_period = 6;
}
```

  * `owner_address`: The address of the resource delegator.
  * `resource`: The type of resource to delegate.
  * `balance`: The amount of resources to delegate, in **sun**.
  * `receiver_address`: The address of the resource recipient.
  * `lock`: Whether to lock the delegation for 3 days.
  * `lock_period`: The lock period for the delegation, in number of blocks. Can be any value in the range (0, 86400]. This parameter is only effective when `lock` is `true`.

### UnDelegateResourceContract

*Undelegates resources.*

```
message UnDelegateResourceContract {
    bytes owner_address = 1;
    ResourceCode resource = 2;
    int64 balance = 3;
    bytes receiver_address = 4;
}
```

  * `owner_address`: The address of the undelegation initiator.
  * `resource`: The type of resource to undelegate.
  * `balance`: The amount of resources to undelegate.
  * `receiver_address`: The address of the resource recipient.

### *(Deprecated)* FreezeBalanceContract

*Stakes TRX to obtain resources (Stake 1.0).*

```
message FreezeBalanceContract {
    bytes owner_address = 1;
    int64 frozen_balance = 2;
    int64 frozen_duration = 3;
    ResourceCode resource = 10;
    bytes receiver_address = 15;
}
```

  * `owner_address`: The address of the contract initiator.
  * `frozen_balance`: The amount of TRX to stake.
  * `frozen_duration`: The staking duration (in days).
  * `resource`: The type of resource to obtain by staking TRX.
  * `receiver_address`: The address of the account that receives the resources.

### *(Deprecated)* UnfreezeBalanceContract

*Unstakes TRX (Stake 1.0).*

```
message UnfreezeBalanceContract {
    bytes owner_address = 1;
    ResourceCode resource = 10;
    bytes receiver_address = 13;
}
```

  * `owner_address`: The address of the contract initiator.
  * `resource`: The type of resource to unstake.
  * `receiver_address`: The address of the account that receives the resources.

### WithdrawBalanceContract

*Withdraws Super Representative rewards.*

```
message WithdrawBalanceContract {
    bytes owner_address = 1;
}
```

  * `owner_address`: The address of the contract initiator.

<a id="trc10-token-contracts"></a>
## TRC-10 Token Contracts

### TransferAssetContract

*Transfers TRC-10 tokens.*

```
message TransferAssetContract {
    bytes asset_name = 1;
    bytes owner_address = 2;
    bytes to_address = 3;
    int64 amount = 4;
}
```

  * `asset_name`: The TRC-10 token ID.
  * `owner_address`: The address of the contract initiator.
  * `to_address`: The destination account address.
  * `amount`: The amount of tokens to transfer.

### AssetIssueContract

*Issues a TRC-10 token.*

```
message AssetIssueContract {
    message FrozenSupply {
      int64 frozen_amount = 1;
      int64 frozen_days = 2;
    }
    bytes owner_address = 1;
    bytes name = 2;
    bytes abbr = 3;
    int64 total_supply = 4;
    repeated FrozenSupply frozen_supply = 5;
    int32 trx_num = 6;
    int32 num = 8;
    int64 start_time = 9;
    int64 end_time = 10;
    int64 order = 11; // the order of tokens of the same name
    int32 vote_score = 16;
    bytes description = 20;
    bytes url = 21;
    int64 free_asset_net_limit = 22;
    int64 public_free_asset_net_limit = 23;
    int64 public_free_asset_net_usage = 24;
    int64 public_latest_free_net_time = 25;
}
```

  * `owner_address`: The token issuer's address.
  * `name`: The token's name.
  * `abbr`: The token's abbreviation.
  * `total_supply`: The total supply.
  * `frozen_supply`: A list of frozen token amounts and their corresponding frozen days.
  * `trx_num`: The number of tokens that can be exchanged for 1 TRX.
  * `num`: The number of tokens required to exchange for 1 TRX.
  * `start_time`: The ICO start time.
  * `end_time`: The ICO end time.
  * `order`: *(Deprecated)*.
  * `vote_score`: *(Deprecated)*.
  * `description`: The token's description.
  * `url`: The token's official URL.
  * `free_asset_net_limit`: The free Bandwidth limit for each account when using this token.
  * `public_free_asset_net_limit`: The total free Bandwidth limit shared by all accounts.
  * `public_free_asset_net_usage`: The amount of free Bandwidth used by all accounts.
  * `public_latest_free_net_time`: The latest time the shared free Bandwidth was used.

### ParticipateAssetIssueContract

*Participates in a TRC-10 token ICO.*

```
message ParticipateAssetIssueContract {
    bytes owner_address = 1;
    bytes to_address = 2;
    bytes asset_name = 3;
    int64 amount = 4;
}
```

  * `owner_address`: The purchaser's address.
  * `to_address`: The token issuer's address.
  * `asset_name`: The token ID.
  * `amount`: The amount of TRX used to purchase tokens, in **sun**.

### UnfreezeAssetContract

*Unfreezes staked tokens that have been issued.*

```
message UnfreezeAssetContract {
    bytes owner_address = 1;
}
```

  * `owner_address`: The token issuer's address.

### UpdateAssetContract

*Updates a token's parameters.*

```
message UpdateAssetContract {
    bytes owner_address = 1;
    bytes description = 2;
    bytes url = 3;
    int64 new_limit = 4;
    int64 new_public_limit = 5;
}
```

  * `owner_address`: The token issuer's address.
  * `description`: The token's new description.
  * `url`: The token's new URL.
  * `new_limit`: The new Bandwidth limit for a single caller.
  * `new_public_limit`: The new public Bandwidth limit for all callers.

<a id="sr-voting-contracts"></a>
## Super Representative & Voting Contracts

### VoteWitnessContract

*Votes for Super Representative candidates.*

```
message VoteWitnessContract {
    message Vote {
      bytes vote_address = 1;
      int64 vote_count = 2;
    }
    bytes owner_address = 1;
    repeated Vote votes = 2;
    bool support = 3;
}
```

  * `owner_address`: The voter's address.
  * `votes`: A list of votes.
      * `vote_address`: The Super Representative candidate's address.
      * `vote_count`: The number of votes for this candidate.
  * `support`: Whether to support. This parameter is currently always `true`.

### WitnessCreateContract

*Applies to become a Super Representative candidate.*

```
message WitnessCreateContract {
    bytes owner_address = 1;
    bytes url = 2;
}
```

  * `owner_address`: The candidate's address.
  * `url`: The candidate's website URL.

### WitnessUpdateContract

*Updates a Super Representative candidate's URL.*

```
message WitnessUpdateContract {
    bytes owner_address = 1;
    bytes update_url = 12;
}
```

  * `owner_address`: The candidate's address.
  * `update_url`: The new website URL.


<a id="proposal-governance-contracts"></a>
## Proposal & Governance Contracts

### ProposalCreateContract

*Creates a proposal.*

```
message ProposalCreateContract {
    bytes owner_address = 1;
    map<int64, int64> parameters = 2;
}
```

  * `owner_address`: The proposer's address.
  * `parameters`: The content of the proposal, represented as key-value pairs.

### ProposalApproveContract

*Approves a proposal. Voting constitutes approval; not voting is considered disapproval.*

```
message ProposalApproveContract {
    bytes owner_address = 1;
    int64 proposal_id = 2;
    bool is_add_approval = 3; // add or remove approval
}
```

  * `owner_address`: The voter's address.
  * `proposal_id`: The proposal's ID.
  * `is_add_approval`: Whether to approve the proposal. `true` for approval, `false` for canceling approval.

### ProposalDeleteContract

*Deletes a proposal.*

```
message ProposalDeleteContract {
    bytes owner_address = 1;
    int64 proposal_id = 2;
}
```

  * `owner_address`: The address of the proposal deleter.
  * `proposal_id`: The proposal's ID.


<a id="smart-contract-contracts"></a>
## Smart Contract Management Contracts

### CreateSmartContract

*Creates a smart contract.*

```
message CreateSmartContract {
    bytes owner_address = 1;
    SmartContract new_contract = 2;
    int64 call_token_value = 3;
    int64 token_id = 4;
}
```

  * `owner_address`: The address of the contract initiator.
  * `new_contract`: Information such as the smart contract's ABI and bytecode.
  * `call_token_value`: The amount of TRC-10 tokens transferred with the contract deployment.
  * `token_id`: The ID of the TRC-10 token being transferred.

### TriggerSmartContract

*Triggers a smart contract.*

```
message TriggerSmartContract {
    bytes owner_address = 1;
    bytes contract_address = 2;
    int64 call_value = 3;
    bytes data = 4;
    int64 call_token_value = 5;
    int64 token_id = 6;
}
```

  * `owner_address`: The address of the contract initiator.
  * `contract_address`: The target contract's address.
  * `call_value`: The amount of TRX transferred with the contract call, in **sun**.
  * `data`: The encoded parameters of the contract method.
  * `call_token_value`: The amount of TRC-10 tokens transferred with the contract call.
  * `token_id`: The ID of the TRC-10 token being transferred.

### UpdateSettingContract

*Updates a smart contract's resource consumption percentage.*

```
message UpdateSettingContract {
    bytes owner_address = 1;
    bytes contract_address = 2;
    int64 consume_user_resource_percent = 3;
}
```

  * `owner_address`: The address of the contract initiator.
  * `contract_address`: The target contract's address.
  * `consume_user_resource_percent`: The updated user resource consumption percentage.

### UpdateEnergyLimitContract

*Adjusts a smart contract's Energy limit.*

```
message UpdateEnergyLimitContract {
    bytes owner_address = 1;
    bytes contract_address = 2;
    int64 origin_energy_limit = 3;
}
```

  * `owner_address`: The address of the contract initiator.
  * `contract_address`: The target contract's address.
  * `origin_energy_limit`: The adjusted Energy limit provided by the contract deployer.

### ClearABIContract

*Clears a smart contract's ABI.*

```
message ClearABIContract {
    bytes owner_address = 1;
    bytes contract_address = 2;
}
```

  * `owner_address`: The address of the contract initiator.
  * `contract_address`: The address of the contract whose ABI is to be cleared.

### UpdateBrokerageContract

*Updates a Super Representative's commission rate.*

```
message UpdateBrokerageContract {
    bytes owner_address = 1;
    int32 brokerage = 2;
}
```

  * `owner_address`: The Super Representative's address.
  * `brokerage`: The new commission rate, ranging from 0 to 100, representing a percentage.

<a id="permission-management"></a>
## Account Permission Management

For detailed information on account permission management, please refer to [Account Permission Management](https://tronprotocol.github.io/documentation-en/mechanism-algorithm/multi-signatures/).
