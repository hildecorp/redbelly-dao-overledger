# Community summary

Plain language summary of the report, ready to share.

Could Redbelly connect to Quant's Overledger? We looked only at public documents. Redbelly and Quant have not announced any partnership or talks, and this research does not suggest any.

Overledger is Quant's platform for reaching many blockchains through one interface. Its self-serve route covers EVM chains, and Redbelly is EVM compatible, so a basic connection, reading Redbelly and sending transactions the sender has signed, looks possible. It is untested, and Overledger describes self-serve as for public permissionless networks, while writing to Redbelly needs a credential. Every Redbelly rule would still apply.

Overledger's Fusion Rollup, its shared layer for moving tokens between chains, did not list Redbelly among the networks connected at its testnet launch, and the docs describe no self-serve way to add a chain. As far as public sources show, that part is not possible yet.

Receptor credentials and Tokeniser's eligibility rules are enforced on Redbelly. In our reading of the docs, they do not follow a token to another chain by themselves, and no public source shows how they would. Keeping regulated assets on Redbelly avoids that gap.

Open questions: whether Overledger would treat Redbelly as self-serve, whether Redbelly passes its health check, which chains The Clearing House network will reach, and Redbelly's own position on bridging. Full report with every source: https://overledger.vercel.app

## As an X thread

1/ The Clearing House picked Quant to power its tokenised deposit network, so people are asking: could Redbelly connect to Quant's Overledger? We read the public docs. Neither announcement mentions Redbelly, and no partnership or talks have been announced.

2/ Overledger reaches many chains through one interface. Its self-serve route covers EVM chains, and Redbelly is EVM compatible. A basic connection for reading data and sending signed transactions looks possible, but it is unconfirmed and untested.

3/ Redbelly's rules still apply on that route. Every account that sends a transaction needs a Redbelly access credential, and Tokeniser checks eligibility on every transfer of its assets.

4/ Overledger's Fusion Rollup, which moves tokens between connected chains, did not list Redbelly at its testnet launch, and the docs describe no self-serve way to add a chain. As far as public sources show, that is not possible yet.

5/ Our reading of the docs: Receptor credentials and Tokeniser rules do not travel with a token to another chain by themselves, so a copy elsewhere follows that chain's rules. Keeping regulated assets on Redbelly avoids the gap.

6/ Still unknown: whether Overledger would treat Redbelly as self-serve, since writing needs a credential; which chains The Clearing House network will reach; and Redbelly's position on bridging. Full report with every source: https://overledger.vercel.app
