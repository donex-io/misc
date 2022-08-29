# Using Bitcoin Core & LND Regtest Mode

Following instructions of

https://medium.com/@bitstein/setting-up-a-bitcoin-lightning-network-test-environment-ab967167594a

More instructions can be found here (note that this uses BTCD instead of Bitcoin Core):

https://dev.lightning.community/tutorial/01-lncli/


## Install Bitcoin Core

Get depencies
	
	sudo apt-get update
	sudo apt-get install -y \
  	autoconf automake build-essential git libtool libgmp-dev \
  	libsqlite3-dev python3 python3-mako net-tools zlib1g-dev libsodium-dev \
 	gettext

Create a bitcoin.conf file:

	nano ~/app-container/.bitcoin/bitcoin.conf

and insert:

	regtest=1
	daemon=1
	txindex=1
	fallbackfee=0.001	# (This is not in the medium article but required to send BTCs)
	rpcuser=ALICE
	rpcpassword=A_PASSWORD
	zmqpubrawblock=tcp://127.0.0.1:28332
	zmqpubrawtx=tcp://127.0.0.1:28333

Add to the bottom of `~/.bashrc` (Note: `~/.bash_profile` was recommened by the Medium article but does not work for Ubuntu Desktop. This can be used instead if you are on SSH).

Open `~/.bashrc`

	nano ~/.bashrc

Add at the bottom:

	export BITCOIN_REGTEST_DIR="$HOME/app-container/.bitcoin"

	alias bitcoind-reg="bitcoind -datadir=$BITCOIN_REGTEST_DIR"
	alias bitcoin-cli-reg="bitcoin-cli -datadir=$BITCOIN_REGTEST_DIR"

Save the file and load it to the shell by

	source ~/.bashrc


## Running Bitcoin Core

Start Bitcoin Core in regtest mode by

	bitcoind-reg

Create a wallet (note: Devation to medium post due to new version of Bitcoin Core)

	 bitcoin-cli-reg createwallet "regWallet"

Start mining more than 100 blocks (Coins are not spendable by miners until there are 100 confirmations)

	bitcoin-cli-reg -generate 101

Check balance by

	bitcoin-cli-reg getbalance


## Setup LND

Get ready to operate several nodes

	mkdir ~/app-container/.lnd1
	mkdir ~/app-container/.lnd2

and create `lnd.conf` file first in lnd1 directory:

	nano ~/app-container/.lnd1/lnd.conf

Insert the following config:

	[Bitcoin]

	bitcoin.active=1
	bitcoin.regtest=1
	bitcoin.node=bitcoind

	[Bitcoind]

	bitcoind.rpchost=localhost
	bitcoind.rpcuser=ALICE
	bitcoind.rpcpass=A_PASSWORD
	bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
	bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333

Now, create `lnd.conf`in the lnd2 directory:
	
	nano ~/app-container/.lnd2/lnd.conf

with the followin config:

	[Application Options]

	listen=0.0.0.0:9734
	rpclisten=localhost:11009
	restlisten=0.0.0.0:8180

	[Bitcoin]

	bitcoin.active=1
	bitcoin.regtest=1
	bitcoin.node=bitcoind

	[Bitcoind]

	bitcoind.rpchost=localhost
	bitcoind.rpcuser=ALICE
	bitcoind.rpcpass=A_PASSWORD
	bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
	bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333

Application options can be

- `rpclisten`: The host:port to listen for the RPC server. This is the primary way an application will communicate with lnd

- `listen`: The host:port to listen on for incoming P2P connections. This is at the networking level, and is distinct from the Lightning channel networks and Bitcoin/Litcoin network itself.

- `restlisten`: The host:port exposing a REST api for interacting with lnd over HTTP. For example, you can get Alice’s channel balance by making a GET request to localhost:8001/v1/channels. 

- `datadir`: The directory that lnd’s data will be stored inside

Setup aliases for both LND nodes in `~/.bashrc`

	nano ~/.bashrc

by adding 

	export LND1_DIR="$HOME/app-container/.lnd1"
	export LND2_DIR="$HOME/app-container/.lnd2"

	alias lnd1="lnd --lnddir=$LND1_DIR"
	alias lncli1="lncli -n regtest --lnddir=$LND1_DIR"

	alias lnd2="lnd --lnddir=$LND2_DIR";
	alias lncli2="lncli -n regtest --lnddir=$LND2_DIR --rpcserver=localhost:11009"

Save the file and oad it to the shell by

	source ~/.bashrc


## Running LND

### lnd1 node

Start lnd1 node by

	lnd1

This terminal will continue to show information about lnd status.

**Open a new terminal window** (you may need to connect the bash file with `source ~/.bashrc`) and create a new wallet by

	lncli1 create

Follow the instructions, then

	lncli1 getinfo

can show the info of current node status.

Do the same with lnd2.

### lnd2 node

Open a new termin (you may need to connect the bash file with `source ~/.bashrc`) and tart lnd2 node by

	lnd2
**Open a new terminal window** (you may need to connect the bash file with `~/.bashrc`) and create a new wallet by

	lncli2 create

Follow the instructions, then

	lncli2 getinfo

Now both LND nodes should be up and running.


## Connecting the Nodes

You can check peers by `lncli1 listpeers` which should be empty. In order to connect both nodes use the `identity_pubkey` of the `getinfo`. With `lnd1` you can connect to `lnd2` by using the `identity_pubkey` of `lnd2` and

	lncli1 connect 0394308702eafc1387dcbb6cf2b2dd88605fa64b9f38531bdc1129467d62ba3778@localhost:9734

(The port of lncli1 may not be set to the proposed default value of the medium post, which said 'If you connect from the second node to the first, you’ll use port `9735`, which is the default.')

Now,

	lncli1 listpeers

should show the lnd2 node. Vise versa, in the terminal of lncli2 you should be able to get the peer of lncli2 by

	lncli2 listpeers

which also reveals the corresponding port.


## Creating a Channel

Generate an Bitcoin address for lnd2 by

	lncli2 newaddress np2wkh

Your address will be returned - for instance

	{
		"address": "2N7vpeF7VfZWLWdC8GoZcVZFyHG5KcAHHxa"
	}

Send 1 BTC to this Bitcoin address

	bitcoin-cli-reg sendtoaddress 2N7vpeF7VfZWLWdC8GoZcVZFyHG5KcAHHxa 1

Get the LND address of lnd1

	lncli1 getinfo

Copy the `identity_pubkey` and open a channel with 100,000 Satoshis by

	lncli2 openchannel 02d58088c0853764505eda515592280b1f4e1299ec35dab290e025f4a9112a2dde 100000

Mine some blocks (at least 3)

	bitcoin-cli-reg -generate 10

Check if it worked:

	lncli1 listchannels

Now, lnd2 has 100,000 Sats in a channel which can be send to lnd1.


## Creating and Sending an Invoice

In order to send 100 Sats from lnd2 to lnd1, lnd1 needs to create an invoice:

	lncli1 addinvoice -amt 100

This creates an invoice which looks like this

	{
		"r_hash": "97ed516103457eeb50e4ff746db92f42df25bbcb8be3afd7a5f6b8c8933ca823",
		"payment_request": "lnbcrt1u1psf23wgpp5jlk4zcgrg4lwk58yla6xmwf0gt0jtw7t3036l4a976uv3yeu4q3sdqqcqzpgsp57ugz2rjh5dp0psxc4mwtem5esz4k5dyqc3sud2hde87l3r4qefts9qyyssqagcxd9l5mwtg5z6ujamn4ffl96l23rv9w5kdwc2qsqarmv6d4clpzfcf6k4pudjp9jt6c4gtwlct9p33udpq797sr7dgg7tvxhvwpwgqlckat0",
		"add_index": "1",
		"payment_addr": "f710250e57a342f0c0d8aedcbcee9980ab6a3480c461c6aaedc9fdf88ea0ca57"
	}

Copy the `payment_request`. Note that request and invoice are the same thing here. The request can be decoded by 

	lncli2 decodepayreq lnbcrt1u1psf23wgpp5jlk4zcgrg4lwk58yla6xmwf0gt0jtw7t3036l4a976uv3yeu4q3sdqqcqzpgsp57ugz2rjh5dp0psxc4mwtem5esz4k5dyqc3sud2hde87l3r4qefts9qyyssqagcxd9l5mwtg5z6ujamn4ffl96l23rv9w5kdwc2qsqarmv6d4clpzfcf6k4pudjp9jt6c4gtwlct9p33udpq797sr7dgg7tvxhvwpwgqlckat0

returning

	{
		"destination": "02d58088c0853764505eda515592280b1f4e1299ec35dab290e025f4a9112a2dde",
		"payment_hash": "97ed516103457eeb50e4ff746db92f42df25bbcb8be3afd7a5f6b8c8933ca823",
		"num_satoshis": "100",
		"timestamp": "1620395464",
		"expiry": "3600",
		"description": "",
		"description_hash": "",
		"fallback_addr": "",
		"cltv_expiry": "40",
		"route_hints": [],
		"payment_addr": "f710250e57a342f0c0d8aedcbcee9980ab6a3480c461c6aaedc9fdf88ea0ca57",
		"num_msat": "100000",
		"features": {
			"9": {
				"name": "tlv-onion",
				"is_required": false,
				"is_known": true
			},
			"14": {	
				"name": "payment-addr",	
				"is_required": true,
				"is_known": true
			},
			"17": {
				"name": "multi-path-payments",
				"is_required": false,
				"is_known": true
			}
		}
	}

Pay the invoice by inserting the `payment_request`

	lncli2 payinvoice lnbcrt1u1psf23wgpp5jlk4zcgrg4lwk58yla6xmwf0gt0jtw7t3036l4a976uv3yeu4q3sdqqcqzpgsp57ugz2rjh5dp0psxc4mwtem5esz4k5dyqc3sud2hde87l3r4qefts9qyyssqagcxd9l5mwtg5z6ujamn4ffl96l23rv9w5kdwc2qsqarmv6d4clpzfcf6k4pudjp9jt6c4gtwlct9p33udpq797sr7dgg7tvxhvwpwgqlckat0

Let’s look up the invoice on the receiving node using the payment hash:

	lncli1 lookupinvoice 97ed516103457eeb50e4ff746db92f42df25bbcb8be3afd7a5f6b8c8933ca823

It should say `Settled: true`.

That's it. Shut down Bitcoin Core and stop lncli1 and lncli2.

	bitcoin-cli-reg stop
	lncli1 stop
	lncli2 stop


## Using LND after power off

0. You may need to load `bashrc` again

	`source ~/.bashrc`

1. Check that Bitcoin Core is running in Regtest mode by just using the command 
	
	`bitcoind-reg`

2. Open terminal for lnd1 and start it by

	`lnd1`

3. Open a new terminal and unlock the wallet by

	`lncli1 unlock`

4. Repeat steps 2 and 3 for `lnd2`.

5. In order to generate new blocks and transfer onchain BTC you need to load the Bitcoin Core wallet

	bitcoin-cli-reg loadwallet "regWallet"


## Forgot the `lncli unlock` password and want to create a new account?

In order to create a new `lnd` account, the old one needs to be removed. To do that, the `data` folder in the `.lnd` directory needs to be removed. Go into the corresponding `.lnd` directory and execute:

	sudo rm -rf data
