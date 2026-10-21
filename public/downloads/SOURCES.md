# Source list

Every factual claim in the report cites one of these sources as S1, S2 and so on. Under each source are the exact words the report relies on. Text snapshots of every page, with capture time and SHA-256, are in `evidence/` (see `evidence/manifest.json`).

**S1. Redbelly DAO Task Board**: TASK-29 brief: Quant Overledger and Redbelly Interoperability Research  
https://taskboard.redbellydao.network/tasks/TASK-29

- "This is feasibility research only. Redbelly and Quant have no announced partnership or talks"
- "Redbelly has not published an official position on bridging"

**S2. Vine, Redbelly Network developer portal**: EVM compatibility and version details  
https://vine.redbelly.network/consensus/evm-compatibility/

- "Redbelly is compatible with the Ethereum Virtual Machine (EVM) and can execute smart contracts written for the EVM."

**S3. Quant, Overledger documentation**: Chapter 5: Connectors  
https://docs.overledger.dev/docs/connectors

- "Six DLT families are available for self-serve onboarding today, you can register a node and call the network without an account-team conversation"
- "Covers every EVM-compatible chain"
- "A DLT family is considered eligible for self-serve if (a) its nodes expose RPC or REST over HTTPS, (b) the RPC requires no security factor beyond an API key, and (c) node identity does not matter to other tenants (so a pool of equivalent nodes can be load-balanced safely)."
- "New network within a supported DLT family, the network is not yet listed by Overledger, but its DLT family is one Overledger already supports for self-serve (EVM, Solana, Cosmos, SUI, Hedera, Aptos). The first POST /nodes call registers both the network and your node for it. This new network will then be available for Overledger users."
- "If public is selected then the user can only add nodes from whitelisted providers. If private is selected then the user can add nodes from any domain."
- "alchemy.com, infura.io, quiknode.pro, chainstack.com, getblock.io, blockdaemon.com, ankr.com"
- "Required, embedded in the URL path (the Gateway forwards the URL as-is), not a header."
- "Any reachable HTTPS URL, self-hosted, custom-provider, on your own infrastructure, anywhere."
- "The Gateway runs a health check using the DLT's standard validation from section 5.1 and, on success, adds the node to the network's load-balancing pool."
- "For networks where node identity matters, typically permissioned DLTs used by regulated consortia and operator-gated public chains, Overledger does not self-serve currently."
- "Implement a DLT checker (health validation + chain identifer lookup) ~2 days"
- "Add per-DLT handling in any apps that need to consume it ~1 day per app"
- "Forwards the payload, returns the native response unchanged."
- "Self-serve Connectors for public, permissionless DLT families."
- "For networks where it does not matter which node a client connects to, i.e. public permissionless networks"
- "Hyperledger Besu (permissioned) Permissioned EVM Used in regulated EVM deployments."
- "Run GET /networks to retrieve the live list."
- "For networks where it does not matter which node a client connects to, i.e. public permissionless networks, Quant Connect lets you register a managed-provider node URL via a single UI form and Overledger lets you register a managed-provider node URL via a single API call. The network then becomes immediately reachable through the Overledger Gateway."
- "Any tenant with access to the network, the node joins the shared load-balancing pool for that network."
- "the node is scoped to your user identity"
- "DLTs that need consortium membership, MSP enrolment, channel agreement, notary trust, privacy-group setup, or any other identity-bound configuration are onboarded through the engagement path"

**S4. Test run for this report**: JSON-RPC calls to Redbelly mainnet and testnet endpoints, 15 October 2026  
https://overledger.vercel.app/evidence/tests/rpc-check.txt (also `evidence/tests/rpc-check.txt` in the repository)

- "https://governors.mainnet.redbelly.network eth_chainId -> {"jsonrpc":"2.0","id":1,"result":"0x97"}"
- "https://rpc.ankr.com/redbelly_mainnet eth_chainId -> {"id":1,"jsonrpc":"2.0","result":"0x97"}"
- "https://governors.mainnet.redbelly.network net_version -> {"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"the method net_version does not exist/is not available"}}"
- "eth_getBlockByNumber -> {"jsonrpc":"2.0","id":1,"result":{"baseFeePerGas":"0xe0fbb4df40c0""

**S5. Vine, Redbelly Network developer portal**: User access  
https://vine.redbelly.network/identity/user-access/

- "Before being granted access to Redbelly Network, each user must claim their access credential from a network accredited issuer before they self enable their account with write access to the network through a specific network smart contract."
- "prove they possess a valid photo identity document (passport) which is verified via biometric checks"

**S6. Quant, Overledger documentation**: Chapter 8: Fusion Rollup  
https://docs.overledger.dev/docs/fusion-rollup

- "Connected DLT networks on testnet launch are: Ethereum Sepolia, Polygon Amoy, Quant's permissioned Besu testnet. The full live list comes from GET /networks/fusion."
- "The bridge and dispute contracts deployed on each connected DLT network. Standard OP Stack contracts, one deployment per chain."
- "Compute Fusion Rollup state roots and post them to all connected DLT networks for settlement"
- "Because Fusion is an optimistic rollup, a withdrawal is not immediately final, there is a dispute window during which a challenger can prove the Fusion Rollup state root invalid."
- "Fusion can map several token contracts to a single rollup-side ERC-20, so deposits from any of those source chains land in one unified balance."
- "Network ID. Exposed for wallets and tools that predate eth_chainId."
- "Supports both public and permissioned DLTs side by side"
- "The Fusion rollups can post transaction data to a single permissioned chain and only state roots to the others"

**S7. Test run for this report**: Calls to the public Overledger server API without an account, 15 October 2026  
https://overledger.vercel.app/evidence/tests/overledger-api-check.txt (also `evidence/tests/overledger-api-check.txt` in the repository)

- "GET https://fusion-rollup.quant.dev/networks/fusion -> HTTP 401 {"status":401,"error":"Missing authorization header.""
- "GET https://fusion-rollup.quant.dev/networks -> HTTP 401 {"status":401,"error":"Missing authorization header.""

**S8. Redbelly Network technical documentation**: Proof by Query  
https://docs.redbelly.network/pages/methods/proof-by-query/

- "a zero knowledge proof based verifier smart contract"
- "State verification and transition, with subsequent publication to the blockchain."

**S9. Tokeniser**: Technology  
https://tokeniser.com/technology

- "Eligibility, identity and your target market determination are enforced at the point of transfer, every time."
- "Deterministic finality settles a transaction in a single round, final the moment it completes."
- "full EVM compatibility connects you to more than 150 networks out of the box"
- "Underneath it runs Redbelly Network"
- "Full EVM compatibility gives connection to more than 150 networks out of the box, with permissioned or permissionless access as your mandate allows."

**S10. The Clearing House**: The Clearing House Partners with Quant to Advance the On-Chain Money Initiative (24 September 2026)  
https://www.theclearinghouse.org/payment-systems/Articles/2026/09/The-Clearing-House-Partners-with-Quant-to-Advance-the--On-Chain-Money-Initiative

- "The Clearing House announced the selection of Quant, a leading provider of programmable money infrastructure, to power its On-Chain Money Initiative, a new interoperable payments network that will enable financial institutions of all sizes to clear and settle tokenized deposit transactions."
- "Quant's technology will enable the network's interoperability, orchestration, and transaction-management layer that coordinates the clearing and settlement of tokenized deposit transactions"
- "providing connectivity to existing fiat payment systems that financial institutions and their customers use every day, including the RTP® and CHIPS® networks"
- "The network is expected to become available to participating institutions in the first half of 2027, with additional details on participation and use cases to be announced as development progresses."

**S11. Quant**: Press release: The Clearing House Partners with Quant to Advance the On-Chain Money Initiative  
https://quant.network/press-releases/the-clearing-house-partners-with-quant-to-advance-the-on-chain-money-initiative/

- "The Clearing House will use Quant's technology to bring on-chain capabilities to its tokenised deposit clearing and settlement network for financial institutions."

**S12. Quant, Overledger documentation**: Start Here  
https://docs.overledger.dev/docs/start-here

- "Overledger is Quant's multi-DLT platform for building applications that span more than one blockchain"
- "Flow Applications turn multi-step business logic (signing, smart-contract deployment, compliance check, payment"
- "You don't manage RPC providers, node failover, or chain-specific clients."

**S13. Quant, Overledger documentation**: Chapter 1: Overview  
https://docs.overledger.dev/docs/overview

- "A Gateway that authenticates clients, routes requests, and orchestrates higher-level workflows."
- "A set of Connectors that abstract individual DLT RPC protocols behind a common interface."
- "A Multi-ledger rollup (the Fusion Rollup) that anchors to multiple blockchains simultaneously, providing one EVM-compatible execution environment with deposits, withdrawals, and cross-chain messaging across every connected L1."
- "Customers and partners can host their own Flow Apps externally, stand up an HTTPS service that implements the Flow App contract, register its URL with the Gateway, and your bespoke regulated workflow becomes a first-class app in Overledger."
- "Managed engagement: you work with Quant's team to onboard a private / consortium network (e.g. Corda, Canton, Fabric) or to add a brand-new DLT family Quant doesn't yet support."
- "A network with controlled write access; "public permissioned" means anyone can read but only allowlisted parties can write."
- "The Rollup connects to a subset of these networks."
- "It applies to every public or permissioned DLT network that the Gateway reaches"
- "Single entry point. Authenticates, routes traffic, hosts Orchestration, fronts the Fusion Rollup."
- "There is one Connector per DLT family"

**S14. Quant, Overledger documentation**: Chapter 6: Flow Apps  
https://docs.overledger.dev/docs/flow-apps

- "today every shipped app is internal"
- "The Flow App catalogue is intentionally not enumerated in these docs"
- "The calling Flow App and the Gateway routing the sub-flow never see private keys. Key material is always under your control."
- "You hold the keys (BYO signing, see chapter 7.2)."
- "Discover what's available for your account through one of two channels"

**S15. Redbelly Network technical documentation**: Home  
https://docs.redbelly.network

- "The Redbelly Network is a layer 1 blockchain, built and optimised for real world asset tokenisation."

**S16. Vine, Redbelly Network developer portal**: Redbelly Network environments  
https://vine.redbelly.network/environments/

- "Network name: Redbelly Network Mainnet RPC URL: https://governors.mainnet.redbelly.network Chain ID: 151"
- "Ankr https://rpc.ankr.com/redbelly_mainnet"
- "RPC URL: https://governors.testnet.redbelly.network Chain ID: 153"

**S17. Vine, Redbelly Network developer portal**: Identity and participation on the network  
https://vine.redbelly.network/identity/

- "all network participants MUST prove they are who they say they are before gaining access"
- "business verification is also available on the network"

**S18. Vine, Redbelly Network developer portal**: Accredited issuers  
https://vine.redbelly.network/identity/accredited-issuers/

- "All accredited issuers are listed in an on chain registry."

**S19. Vine, Redbelly Network developer portal**: Business verification  
https://vine.redbelly.network/business-verification/

- "To be verified, businesses need to prove they are an incorporated entity to a network accredited issuer."

**S20. Vine, Redbelly Network developer portal**: Becoming a node operator  
https://vine.redbelly.network/nodes/become-operator/

- "Node operators MUST have network access for 2 accounts and provide their public address when applying to run a node."
- "Applicants will be selected based upon their previous experience, location and commitment to the Redbelly Project."

**S21. Vine, Redbelly Network developer portal**: Bridged tokens: Celer cBridge  
https://vine.redbelly.network/bridged-tokens/celer/

- "RBNT bridges out from Redbelly to Ethereum and BNB Chain, not back."
- "Ethereum 0x063a1D5BFEAb213c9c12f47b704fccf81D60983e wRBNT Wrapped RBNT 18"

**S22. Vine, Redbelly Network developer portal**: Bridged tokens: LayerZero  
https://vine.redbelly.network/bridged-tokens/layerzero/

- "Tokens on Redbelly Network that can be bridged to other chains via LayerZero, using Stargate, and vice versa."

**S23. Vine, Redbelly Network developer portal**: Bridged tokens: Lucid Labs  
https://vine.redbelly.network/bridged-tokens/lucidlabs/

- "Tokens on Redbelly Network that can be bridged to other chains via Lucid Labs, and vice versa. Powered by Polymer and LayerZero."
- "Ethereum 0xb45fFB51984d626Ee758b336C61Cf20990c6bF13 WRBNT Wrapped RBNT 18"

**S24. Redbelly Network technical documentation**: Receptor overview  
https://docs.redbelly.network/pages/receptor/

- "Receptor is Redbelly's native digital identity and verifiable credential protocol."
- "Receptor is built on the W3C verifiable credential data model, providing a standardised and interoperable foundation for identity verification and eligibility criteria assurance."

**S25. Vine, Redbelly Network developer portal**: Eligibility  
https://vine.redbelly.network/identity/eligibility/

- "Redbelly supports two distinct credential types, or methods, that can be used to perform eligibility criteria checks:"

**S26. Redbelly Network technical documentation**: Selective Disclosure  
https://docs.redbelly.network/pages/methods/selective-disclosure/

- "As selective disclosure involves disclosing information to the Verifier, it can only be used off-chain."
- "Selective Disclosure involves using credentials that implement BBS+ signatures."

**S27. Redbelly Network technical documentation**: Eligibility SDK for Redbelly Network  
https://docs.redbelly.network/pages/eligibility-sdk/eligibility-sdk/

- "Redbelly Mainnet did:receptor:redbelly:mainnet:31AAH8sSaGd6fpnG1TcB6yQ4UZnNeyHzTk5aM2P7rjv"

**S28. Vine, Redbelly Network developer portal**: Eligibility checks (smart contracts)  
https://vine.redbelly.network/smart-contracts/eligibility-checks/

- "Eligibility checks can be used to control access to your dApp or smart contract's functions or when specific smart contract functions are called to help meet your compliance requirements."

**S29. Tokeniser**: Automated compliance  
https://tokeniser.com/product/superpowers/automated-compliance

- "Before any trade proceeds, the investor's identity, eligibility (including wholesale or sophisticated status where required) and your limits are verified automatically."

**S30. Tokeniser**: Secondary transfer  
https://tokeniser.com/product/superpowers/secondary-transfer

- "every transfer is recorded on your register in real time"

**S31. Tokeniser**: Collateral mobility  
https://tokeniser.com/product/superpowers/collateral-mobility

- "Investors pledge units as security, and the units remain locked until the loan is repaid."

**S32. Celer Network blog**: Celer Announces cBridge Support for Redbelly (1 August 2025)  
https://blog.celer.network/2025/08/01/celer-announces-cbridge-support-for-redbelly/

- "Celer is supporting asset and token bridging initially via a pegged bridge method"

**S33. Redbelly Network on X**: Wrapped RBNT Token is now live on Ethereum Mainnet (14 February 2025)  
https://x.com/RedbellyNetwork/status/1890340030197166112

- "Wrapped RBNT Token is now live on Ethereum Mainnet."
- "0xb45ffb51984d626ee758b336c61cf20990c6bf13"

**S34. Redbelly DAO Community Task Board**: TASK-08 bridge integration guide (selected entry)  
https://github.com/Redbelly-DAO-Community-Taskboard/TASK-08-bridge-integration-guide

- "Redbridge is a lock-and-mint bridge"
- "Yes, on Mainnet dedicated "Redbelly Mainnet" deployment"

**S35. TASK-08 entry, public repository**: Bridging Ethereum Sepolia to Redbelly Testnet: technical guide  
https://github.com/tycayomide/redbelly-testnet-bridge/blob/main/TECHNICAL_GUIDE.md

- "as of this writing no major interoperability protocol has deployed core messaging infrastructure (endpoints, gateways, or guardian sets) to Redbelly Testnet specifically"
- "LayerZero went live on Redbelly Mainnet"

**S36. Redbelly DAO Community Task Board**: TASK-16 Cross-Chain Recovery Playbook (selected entry, PDF)  
https://github.com/Redbelly-DAO-Community-Taskboard/TASK-16-cross-chain-recovery-playbook/blob/main/deliverable/Redbelly-task-16-revised.pdf

- "Because the official Redbelly bridges (Reddex and Lucid) currently only support bridging USDC and USDT from BNB Chain"

**S37. Quant, Overledger documentation**: Chapter 9: Overledger Firewall  
https://docs.overledger.dev/docs/overledger-firewall

- "Overledger maintains the binding between each user and their authorised on-chain address(es) off-chain, so policies expressed against a user translate into on-chain address allowlists at the contracts that enforce them."
- "Token allowlist entries are governance-controlled (Quant Safe signers), not per-deployer, they apply to all users of the bridge."

**S38. Quant, Overledger API reference**: Overledger Server API reference  
https://docs.overledger.dev/reference

- "List Fusion Rollup connected networks"
