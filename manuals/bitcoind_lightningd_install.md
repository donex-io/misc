# Setting up Ubuntu with bitcoind and lightningd

!!! First part outdated! Follow instead: https://lightning.readthedocs.io/INSTALL.html#to-build-on-ubuntu !!!

The following commands should set up a complete environment on Ubuntu for using c-lightning in conjunction with Python RPC (and Plugins)

The installation steps for bitcoind (Bitcoin core) and lightningd (c-lightning) are taken from: https://lightning.readthedocs.io/INSTALL.html#to-build-on-ubuntu

The bitcoinlib (for Python) is taken from: https://pypi.org/project/bitcoinlib/ (python-bitcoinlib from https://github.com/petertodd/python-bitcoinlib seems outdated?! Not sure if it's predecessor...)

The pyln-client part is taken from: https://pypi.org/project/pyln-client/ (pylightning from https://pypi.org/project/pylightning/ is outdated)

## Start

Go to home directory

    cd

Update apt-get

    sudo apt-get update
    
## bitcoind

Get depencies

    sudo apt-get install -y \
    autoconf automake build-essential git libtool libgmp-dev \
    libsqlite3-dev python3 python3-mako net-tools zlib1g-dev libsodium-dev \
    gettext
    
Install bitcoind via snapd

    sudo apt-get install snapd
    sudo snap install bitcoin-core
    sudo ln -s /snap/bitcoin-core/current/bin/bitcoin{d,-cli} /usr/local/bin/
    
## lightningd

lightningd is installed via make

First clone lightning

    git clone https://github.com/ElementsProject/lightning.git
    cd lightning
    
The following two commands are recommended for development (according to https://lightning.readthedocs.io/INSTALL.html#to-build-on-ubuntu) but only the first one worked for me. The second one threw an error but make further below worked anyway.

    sudo apt-get install -y valgrind python3-pip libpq-dev
    sudo pip3 install -r requirements.txt
    
Configure (you should now be in $/lightning)

    ./configure
    
Or for development

    ./configure --enable-developer
    
// Robin's additions:
    
    sudo apt install jq

Build lightning via make and make install

    make
    sudo make install
    
After finishing this, your lightningd is ready to go. You can run a pre-installed shell script to setup a regtest environment. This script already sets the correct config file settings for both bitcoind and lightningd. Run the script via (you should still be in $/lightning). (You may need to start `bitcoind` before.)

    . contrib/startup_regtest.sh

The dot command (".", alternatively you can use the "source" command) temporarily creates new shell commands through the shell script. Now one of these new commands can be run to create a number of instances of lightning nodes (3 nodes in this case):

    start_ln 3

Now three instances of lightning nodes should have started plus bitcoind should have been started if it wasn't already running.

Check whether you get info back from the different lightning nodes over the following shell-based RPC commands

    l1-cli getinfo
    l2-cli getinfo
    l3-cli getinfo

Check the info from your bitcoin node

    bt-cli -getinfo


## Shutdown

To shut down the running lightning nodes, run

    stop_ln
