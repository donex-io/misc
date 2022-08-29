# Installing Bitcoind Core & LND

## Before you start

You may want to add a sudo user
```shell
adduser username

usermod -aG sudo username

su - username
```
and update the system
```shell

sudo apt-get update

sudo apt update
```

Commands which are not required are indented.


## Bitcoin Core

### Installation

Quick installation following 
https://bitcoin.org/en/full-node#linux-instructions 
(check for version!)

```shell
curl https://bitcoin.org/bin/bitcoin-core-22.0/bitcoin-22.0-x86_64-linux-gnu.tar.gz --output bitcoin-22.0-x86_64-linux-gnu.tar.gz

tar xzf bitcoin-22.0-x86_64-linux-gnu.tar.gz

sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-22.0/bin/*

su -c 'install -m 0755 -o root -g root -t /usr/local/bin bitcoin-22.0/bin/*'
```

Bitcoin Core installation guide (long version) following
https://stopanddecrypt.medium.com/a-complete-beginners-guide-to-installing-a-bitcoin-full-node-on-linux-2021-edition-46bf20fbe8ff

```shell
sudo apt-get install git

mkdir -p ~/code && cd ~/code

git clone https://github.com/bitcoin/bitcoin.git


sudo apt-get install build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 libevent-dev

sudo apt-get install libboost-system-dev libboost-filesystem-dev libboost-test-dev libboost-thread-dev

sudo apt-get install libsqlite3-dev

sudo apt-get install libminiupnpc-dev

sudo apt-get install libzmq3-dev

sudo apt-get install libqt5gui5 libqt5core5a libqt5dbus5 qttools5-dev qttools5-dev-tools

sudo apt-get install libqrencode-dev

	# ( May not be required )
	sudo apt-get install libdb++-dev			


mkdir -p ~/code/bitcoin && cd ~/code/bitcoin

./contrib/install_db4.sh `pwd`


	# ( Check version )
	git tag						

	# ( to quit )
	q						

# ( or current version )
git checkout tags/v0.21.0				

./autogen.sh

export BDB_PREFIX='/home/USER/code/bitcoin/db4'	# replace 'USER' by user name

./configure BDB_LIBS="-L${BDB_PREFIX}/lib -ldb_cxx-4.8" BDB_CFLAGS="-I${BDB_PREFIX}/include"

make

sudo make install
```

### Configuration

Example:

https://github.com/bitcoin/bitcoin/blob/master/share/examples/bitcoin.conf

```
mkdir ~/.bitcoin

cd ~/.bitcoin

nano bitcoin.conf
```

Include the following configurations in `~/.bitcoin/bitcoin.conf`:
```
# Run on the testnet network
testnet=1

# Run on a signet network
#signet=0

# Run a regression test network
#regtest=0

# Required for LND
txindex=1

# server=1 tells Bitcoin-Qt and bitcoind to accept JSON-RPC commands
server=1

# Start as daemon
daemon=1

# On client-side, you add the normal user/password pair to send commands:
rpcuser=ALICE
rpcpassword=A_PASSWORD

# Communication with LND
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333

# If only tor shall be used:
#onlynet=onion

# Options only for mainnet
[main]

# Options only for testnet
[test]

# Options only for signet
[signet]

# Options only for regtest
[regtest]
```
Exit nano by `Crtl + O` > `Enter` > `Crtl + X`.


## LND 

### Installation

LND installation guide:

https://stopanddecrypt.medium.com/a-complete-beginners-guide-to-installing-a-lightning-node-on-linux-2021-edition-ece227cfc35d#b471

```shell
cd ~/code

wget https://dl.google.com/go/go1.15.6.linux-amd64.tar.gz

sudo tar -C /usr/local -xzf go1.15.6.linux-amd64.tar.gz


echo "export PATH=$PATH:~/go/bin:/usr/local/go/bin" >> ~/.bashrc

# close shell and open new one

	# check if path is correct by, answer should be /home/USER/go/bin/
	echo ~/go/bin/$path

#Lukas: which directory?

git clone https://github.com/lightningnetwork/lnd

cd ~/code/lnd

	# ( Check version )
	git tag		# Why don't I see the current version?		
		
	# ( to quit )
	q						

# ( or current version ) Lukas: What does current version mean?
git checkout tags/v0.12.1-beta				

make install

```

### Configuration

Example:

https://github.com/lightningnetwork/lnd/blob/master/sample-lnd.conf


```shell
mkdir ~/.lnd

cd ~/.lnd

nano lnd.conf
```

Include the following configurations in `~/.lnd/lnd.conf`:
```
## LND Settings

# Lets LND know to run on top of Bitcoin (as opposed to Litecoin)
bitcoin.active=true
bitcoin.testnet=true
#bitcoin.mainnet=true

# Lets LND know you are running Bitcoin Core (not btcd or Neutrino)
bitcoin.node=bitcoind


## Bitcoind Settings

# Tells LND what User/Pass to use to RPC to the Bitcoin node
bitcoind.rpcuser=ALICE
bitcoind.rpcpass=A_PASSWORD

# Allows LND & Bitcoin Core to communicate via ZeroMQ
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333


## Zap Settings

# Tells LND to listen on all of your computer's interfaces
# This could alternatively be set to your router's subnet IP
tlsextraip=0.0.0.0

# Tells LND where to listen for RPC messages
# This could also be set to your router's subnet IP
rpclisten=0.0.0.0:10009


## Tor Settings

[Tor]
tor.active=true
tor.v3=true
tor.streamisolation=true
```
Exit nano by Crtl + O > Enter > Crtl + X.


## Usage

### Bitcoind
Start Bitcoin Core simply by `bitcoind`. Bitcoin Core then starts syncing the blockchain. You can check the status by `bitcoin-cli -getinfo`. It provides the interaction with Bitcoin Core. You can check additional possible commands by entering `bitcoin-cli`.

### LND

Setting the macaroonpath in `~/.bashrc` by adding (or similarly for mainnet)

`alias lncli-testnet="lncli --macaroonpath=~/.lnd/data/chain/bitcoin/testnet/admin.macaroon"`

at the end of the file. Then, open new terminal.


## Using tor

Note: Syncing the blockchain via Tor takes a while. Consider to sync the blockchain without Tor first.

Tor setup guide:

https://8bitcoin.medium.com/how-to-run-a-bitcoin-full-node-over-tor-on-an-ubuntu-linux-virtual-machine-bdd7e9415a70

```shell
sudo apt install tor

sudo sh -c "echo 'ControlPort 9051' >> /etc/tor/torrc"

sudo systemctl restart tor

# Replace 'username' by your username:
sudo usermod -a -G debian-tor username
```
Restart your system. Add `onlynet=onion` to `bitcoin.conf`. Start Bitcoin Core by `bitcoind`. Check if running correctly by `bitcoin-cli getnetworkinfo` which should show 

```
{
	"name": "ipv4",
	"limited": true,
	"reachable": false,
	"proxy": "",
	"proxy_randomize_credentials": false
}
...
{
	"name": "onion",
	"limited": false,
	"reachable": true,
	"proxy": "127.0.0.1:9050",
	"proxy_randomize_credentials": true
}
```


## Notes:

If you want to check the files in your directory, use `ls -a`.

Continue running during sleep: 
```
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

systemctl restart systemd-logind.service
```
Undo by: `sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target`
