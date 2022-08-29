## Python RPC libraries for bitcoind and lightningd 

After following the installation steps of bitcoind and lightningd with the manual bitcoind_lightningd_install.md, we now want to run bitcoind and lightningd over a Python script which requires python-bitcoinrpc & pyln-client to be installed first.

Install python-bitcoinrpc 

    pip3 install python-bitcoinrpc

Install pyln-client

    pip3 install pyln-client

Then we need to copy the shell script startup_regtest_mod.sh and the Python script setup_close_payment_channels.py into our home folder on the Linux machine where we installed bitcoind and lightningd. 

The shell script is a version of the script startup_regtest.sh under the folder $HOME/lightning/contrib, which I slightly modified. I added the creation of a bitcoin.conf file, which is necessary for python-bitcoinrpc to work. I also added the standard startup of five lightning nodes when the script is run. 

Let's change into our home folder (in case we are not already there)

    cd

Then run the shell script with the source ('.') command

    . startup_regest_mod.sh
    
We should see bitcoind and the lightning nodes starting up. If there is a wallet problem with bitcoind, you may ignore it. We will try to fix this with the following Python script.

Now, let's run the Python script that is meant to create a payment channel ring between the nodes with an even balance on both sides of each payment channel. We run it the argument 'setup'

    python3 setup_close_payment_channels.py 'setup'
    
There is a chance that the Python script fails at some point. There are still  some bugs and some timing issues in there. In case this happens, just run the script with the option 'setup' again.

If we want to close the payment channels again and disconnect the nodes we can run the script with the argument 'close'

    python3 setup_close_payment_channels.py 'close'
    
Also here, some timing issues can occur. In case this happens, just rerun the script with the argument 'close' again.
