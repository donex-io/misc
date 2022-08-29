# script to setup payment channels after running . contrib/startup_regtest_mod.sh and then start_ln "X" command. X should be greater or equal to the number of nodes defined below

##########################################
# conduct imports
import json
import sys
import time
from random import randint

# load bitcoin rpc library
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# load lightning rpc library
from pyln.client import LightningRpc
##########################################

##########################################
# create RPC connections

# setup JSON-rpc connection with bitcoin-cli, 'admin' is set in bitcoin.conf
bt_cli = AuthServiceProxy("http://%s:%s@127.0.0.1:18443"%('admin', 'admin'))

# setup rpc connections with the lightning nodes
number_of_nodes = 5
ln_cli = []
for i in range(0, number_of_nodes):
    ln_cli.append(LightningRpc("/tmp/l".strip()+str(i+1).strip()+"-regtest/regtest/lightning-rpc".strip()))
###########################################

###########################################
# function definitions

# function to make sure some wallet is loaded in bt-cli. If not, load or create wallet with walletname 'default'
def check_for_bt_wallet():
    try:
        walletname = bt_cli.getwalletinfo()['walletname']
        print("\nWallet '",walletname,"' is already loaded.")
    except:
        walletname = "default"
        print("\nNo wallet is loaded. Try to load wallet '", walletname, "'.")
        try:
            loaded_wallet = bt_cli.loadwallet(walletname)
            print("Existing wallet ",loaded_wallet['name']," has been loaded.")
        except:
            print("No existing wallet with the name ", walletname, ".")
            created_wallet = bt_cli.createwallet(walletname)
            print("Wallet ",created_wallet['name']," has been created.")

# function to generate (mine) number_of_blocks blocks to fund the wallet and check balance before and after
def mine_new_blocks(number_of_blocks):
    print("\nMine", number_of_blocks, "new blocks...")
    bt_cli.generatetoaddress(number_of_blocks, bt_cli.getnewaddress())
    print("bt-cli balance after mining: ", bt_cli.getbalance(), " BTC")

# function to give time to let ln nodes gossip and get newest blockchain state
def give_time(number_of_seconds):
    print("\nGive time to let ln nodes gossip and get newest blockchain state:", number_of_seconds, "s")
    time.sleep(number_of_seconds)

# function to mine new blocks over bt and give time to let ln nodes gossip and get newest blockchain state
def mine_and_give_time():
    mine_new_blocks(101) # mine 101 new blocks
    give_time(20) # give 10 s time

# function to sum up all outputs of ln nodes to a total node balance
def ln_node_balance(node_number):
    outputs = ln_cli[node_number].listfunds()['outputs']
    total_balance = 0
    for x in outputs:
        total_balance += x['value']/1E8# total_balance is in BTC, 'value' from listfunds is in sat, 'amount' in msat
    return total_balance

def print_ln_node_balances():
    print("\nln node balances:")
    for i in range(0, number_of_nodes):
        print("ln node", i, "with id", ln_cli[i].getinfo()['id'], "has a balance of: ", ln_node_balance(i), " BTC") #the balances are not always up-to-date

# fund a single ln node from bt wallet
def fund_ln_node(node_number, amount):
    bt_cli.sendtoaddress(ln_cli[node_number].newaddr()['bech32'], amount) # amount in BTC

# fund all existing ln nodes with a specific minimum amount
def fund_all_ln_nodes(minimum_amount):
    print("")
    funding_took_place = 0
    for i in range(0, number_of_nodes):
        funding_amount = round(minimum_amount - ln_node_balance(i), 8)
        if funding_amount > 0:
            give_time(1)
            fund_ln_node(i, funding_amount)
            print("Funded", funding_amount, "BTC to node", i,".")
            funding_took_place += 1
        else:
            print("Node", i, "already sufficiently funded.")
    if funding_took_place != 0:
        mine_and_give_time()

# print channel balances between node_a and node_b from a's perspective
def print_channel_balances(node_a, node_b):
    channels_a = ln_cli[node_a].listfunds()['channels']
    node_id_b = ln_cli[node_b].getinfo()['id']
    for x in channels_a:
        if x['peer_id'] == node_id_b:
            total_channel_balance = int(x['amount_msat'])
            local_channel_balance = int(x['our_amount_msat'])
            remote_channel_balance = total_channel_balance - local_channel_balance
            channel_rebalancing_amount = round((2*local_channel_balance - total_channel_balance)/2, 8) # our_amount has to be seen from a's perspective
            print("\nPayment channel from node", node_a, "to", node_b,":")
            print("Total channel balance: ", total_channel_balance*1E-3, " sat.")
            print("Local channel balance: ", local_channel_balance*1E-3, " sat.")
            print("Remote channel balance: ", remote_channel_balance*1E-3, " sat.")
            print("channel_rebalancing_amount: ", channel_rebalancing_amount*1E-3, " sat.")
    if len(channels_a) != 0:
            return 1
    else:
            return 0

# print all existing payment channels
def print_all_existing_channels():
    number_of_channels = 0
    for i in range(0, number_of_nodes):
        if i==number_of_nodes-1:
            number_of_channels += print_channel_balances(i, 0)
        else:
            number_of_channels += print_channel_balances(i, (i+1))
    if number_of_channels == 0:
        print("\nNo existing channels")
    return number_of_channels

# function to connect from node_a (e.g. 0) to node_b (e.g. 1)
def connect_ln_nodes(node_a, node_b):
    ln_cli[node_a].connect(ln_cli[node_b].getinfo()['id']+"@localhost:"+str(7070 + (node_b+1) * 101))

# connect the channels to form an ln node ring
def connect_ln_node_ring():
    print("\nConnect ln node ring...")
    for i in range(0, number_of_nodes):
        if i==number_of_nodes-1:
            connect_ln_nodes(i, 0)
        else:
            connect_ln_nodes(i, (i+1))
    give_time(10)

def print_ln_node_connections():
    for i in range(0, number_of_nodes):
        print("\nln node", i, "with id", ln_cli[i].getinfo()['id'], "\nis connected to:")
        for x in ln_cli[i].listpeers()['peers']:
            print(x['id'])

# fund payment channel from node_a (e.g. 0) to node_b (e.g. 1) with amount
def fund_payment_channel(node_a, node_b, amount): # amount is in sat
    try:
        ln_cli[node_a].fundchannel(ln_cli[node_b].getinfo()['id'], amount) #fundchannel hangs but does not fail sometimes
    except:
        print("Could not fund channel. No funds or channel exists already?")

# create payment channels between all nodes in the ring and fund the channels
def fund_ln_payment_channel_ring(funding_amount):
    print("\nFund ln payment channel ring...")
    # find out whether payment channel already exists or else fund new channel
    for i in range(0, number_of_nodes):
        channels_a = ln_cli[i].listfunds()['channels']
        has_payment_channel = 0
        if i==number_of_nodes-1:
            for x in channels_a:
                node_id_b = ln_cli[0].getinfo()['id']
                if x['peer_id'] == node_id_b:
                    has_payment_channel = 1
            if has_payment_channel == 0:
                fund_payment_channel(i,0,funding_amount)
        else:
            for x in channels_a:
                node_id_b = ln_cli[i+1].getinfo()['id']
                if x['peer_id'] == node_id_b:
                    has_payment_channel = 1
            if has_payment_channel == 0:
                fund_payment_channel(i,i+1,funding_amount)
    mine_and_give_time()

# rebalance payment channel from node_b to node_a
def rebalance_payment_channel(node_a, node_b):
    channels_a = ln_cli[node_a].listfunds()['channels']
    node_id_b = ln_cli[node_b].getinfo()['id']
    for x in channels_a:
        if x['peer_id'] == node_id_b:
            total_channel_balance = int(x['amount_msat'])
            local_channel_balance = int(x['our_amount_msat'])
            remote_channel_balance = total_channel_balance - local_channel_balance
            channel_rebalancing_amount = int(round((2*local_channel_balance - total_channel_balance)/2, 8)) # our_amount has to be seen from a's perspective
            if channel_rebalancing_amount > 0:
                invoice = ln_cli[node_b].invoice(channel_rebalancing_amount,randint(0, 1E6),"rebalance")
                print("\nInvoice from node ", node_b, "to node", node_a, ": ", invoice['bolt11'])
                ln_cli[node_a].pay(invoice['bolt11'])
                print("paid!")
                give_time(2)
            elif channel_rebalancing_amount < 0:
                invoice = ln_cli[node_a].invoice(-channel_rebalancing_amount,randint(0, 1E6),"rebalance")
                print("\nInvoice from node ", node_a, "to node", node_b, ": ", invoice['bolt11'])
                ln_cli[node_b].pay(invoice['bolt11'])
                print("paid!")
                give_time(2)
            else:
                return

# make 50:50 balance in channels
def rebalance_ln_payment_channel_ring():
    print("\nRebalance ln payment channel ring...")
    for i in range(0, number_of_nodes):
        if i==number_of_nodes-1:
            rebalance_payment_channel(i, 0)
        else:
            rebalance_payment_channel(i, (i+1), )
    mine_and_give_time()

# the following part with the channel closing functions does not work yet

# graciously close payment channel
def close_payment_channel(node_a, node_b): # amount is in sat
    channels_a = ln_cli[node_a].listfunds()['channels']
    node_id_b = ln_cli[node_b].getinfo()['id']
    for x in channels_a:
        if x['peer_id'] == node_id_b:
            short_channel_id = x['short_channel_id'] # look up channel id
            print("\nTrying to close channel", short_channel_id)
    try:
        #ln_cli[node_a].close(short_channel_id)
        channel_close_return = ln_cli[node_a].close(node_id_b)
        print(channel_close_return)
    except:
        print("\nAn error occured in lightning-close function. Maybe no channel to close?")

# close all existing payment channels
def close_all_existing_payment_channels():
    for i in range(0, number_of_nodes):
        if i==number_of_nodes-1:
            close_payment_channel(i, 0)
        else:
            close_payment_channel(i, (i+1))
    mine_and_give_time()



## high level functions

def setup_payment_channel_ring(): # there are still problems with invoice and pay some times

    print_ln_node_connections()
    connect_ln_node_ring()
    print_ln_node_connections()

    print_ln_node_balances()
    fund_all_ln_nodes(1) #fund every node so it has a balance of 1 BTC
    print_ln_node_balances()

    print_all_existing_channels()
    fund_ln_payment_channel_ring(100000) #funding amount in sat
    rebalance_ln_payment_channel_ring()
    print_all_existing_channels()

def close_payment_channel_ring():

    print_ln_node_connections()
    print_all_existing_channels()
    close_all_existing_payment_channels()
    print_all_existing_channels()
    print_ln_node_connections()

###########################################


###########################################
# start of actual script

check_for_bt_wallet()

if sys.argv[1] == "setup":
    setup_payment_channel_ring()
elif sys.argv[1] == "close":
    close_payment_channel_ring()
elif sys.argv[1] == None:
    print("No arguments passed. Pass \"setup\" or \"close\" as arguments")
else:
    print("Wrong argument(s)", sys.argv, "passed. Pass \"setup\" or \"close\" as arguments")

###########################################
