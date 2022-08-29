import rpc_pb2 as lnrpc
import rpc_pb2_grpc as lnrpc_grpc
import invoices_pb2 as lninvoices
import invoices_pb2_grpc as lninvoices_grpc
import router_pb2 as lnrouter
import router_pb2_grpc as lnrouter_grpc

import grpc
import os
import codecs
import time

import socket

# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

# Lnd cert is at ~/.lnd/tls.cert on Linux and
# ~/Library/Application Support/Lnd/tls.cert on Mac
cert = open(os.path.expanduser('~/.lnd/tls.cert'), 'rb').read()
creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', creds)
lightning_stub = lnrpc_grpc.LightningStub(channel)
router_stub = lnrouter_grpc.RouterStub(channel)

# Lnd admin macaroon is at ~/.lnd/data/chain/bitcoin/simnet/admin.macaroon on Linux and
# ~/Library/Application Support/Lnd/data/chain/bitcoin/simnet/admin.macaroon on Mac
with open(os.path.expanduser('~/.lnd/data/chain/bitcoin/testnet/admin.macaroon'), 'rb') as f:
    macaroon_bytes = f.read()
    macaroon = codecs.encode(macaroon_bytes, 'hex')
identity_pubkey = lightning_stub.GetInfo(lnrpc.GetInfoRequest(), metadata=[('macaroon', macaroon)]).identity_pubkey

# Open server socket
PORT = 50000        # The port used by the server for incoming connections
IP = '178.18.244.121' # Lukas' IP address of the server
#IP = '144.91.107.101' # Robin's IP address of the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

    # Start server
    server.bind((IP, PORT))
    server.listen()

    # Listen and reply in infinite loop
    while True:
        print('Wait for payment request...')
        conn, addr = server.accept() # start accepting clients on the socket
        print('Accepted connection')
        with conn:
            print('Connected by', addr)
            while True:
                remote_payment_request = conn.recv(2048) # receive payment request over socket
                if not remote_payment_request: # break out of while loop in case no data is sent
                    print('Close connection')
                    break
                print ('\n', '\n', 'balance: ', lightning_stub.ChannelBalance(lnrpc.ChannelBalanceRequest(), metadata=[('macaroon', macaroon)]).local_balance.sat) # displays the sum of local channel balances
                print ('\n', 'Received payment request')
                request = lnrouter.SendPaymentRequest(
                    payment_request=remote_payment_request,
                    timeout_seconds= 5,
                ) # define payment details
                for response in router_stub.SendPaymentV2(request, metadata=[('macaroon', macaroon)]): # send the payment
                    print('SendPaymentV2 attempt')
                print ('\n', 'Conducted payment')
                conn.sendall(response.payment_hash.encode('UTF-8')) # send payment hash as a confirmation
