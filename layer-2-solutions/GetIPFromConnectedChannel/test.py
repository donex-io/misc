import rpc_pb2 as lnrpc
import rpc_pb2_grpc as rpcstub
import grpc
import os
import codecs
import invoices_pb2 as invoicesrpc, invoices_pb2_grpc as invoicesstub
# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

# Lnd cert is at ~/.lnd/tls.cert on Linux and
# ~/Library/Application Support/Lnd/tls.cert on Mac
cert = open(os.path.expanduser('~/.lnd/tls.cert'), 'rb').read()
creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', creds)

stub = rpcstub.LightningStub(channel)

with open(os.path.expanduser('~/.lnd/data/chain/bitcoin/testnet/admin.macaroon'), 'rb') as f:
    macaroon_bytes = f.read()
    macaroon = codecs.encode(macaroon_bytes, 'hex')

#request = lnrpc.WalletBalanceRequest()

#get WalletBalance
#response = stub.WalletBalance(ln.WalletBalanceRequest(), metadata=[('macaroon', macaroon)])

request = lnrpc.ListChannelsRequest(active_only=1)

response = stub.ListChannels(request, metadata=[('macaroon', macaroon)])

print(response)

index = input('Select payment address')

hash = bytes.fromhex(response[index])

request = lnrpc.Invoice(
memo='TEST',
value=2500,
payment_addr=bytes.fromhex('0226918484c01ac81355c71e8030f0b997f7d778d1782b26ae6c5feb832fc4b118')
)

response = stub.AddInvoice(request, metadata=[('macaroon', macaroon)])
print(response)

#response = stub.WalletBalance(ln.WalletBalanceRequest())
#print(response.total_balance)
