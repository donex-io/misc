// LND used with JS
const fs = require('fs');
const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');
const loaderOptions = {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
};

const async = require('async');
const _ = require('lodash');
const ByteBuffer = require('bytebuffer');

process.env.GRPC_SSL_CIPHER_SUITES = 'HIGH+ECDSA';

const packageDefinition = protoLoader.loadSync(['router.proto', 'lightning.proto', 'invoices.proto', 'signer.proto', 'lncli.proto', 'autopilot.proto', 'verrpc.proto'], loaderOptions);
const lnrpc = grpc.loadPackageDefinition(packageDefinition).lnrpc;
const routerrpc = grpc.loadPackageDefinition(packageDefinition).routerrpc;
const invoicesrpc = grpc.loadPackageDefinition(packageDefinition).invoicesrpc;



// Setup credentials

// LND1

const macaroon1 = fs.readFileSync('/home/rob/app-container/.lnd1/data/chain/bitcoin/regtest/admin.macaroon').toString('hex');
const lndCert1 = fs.readFileSync("/home/rob/app-container/.lnd1/tls.cert");
const sslCreds1 = grpc.credentials.createSsl(lndCert1);
const macaroonCreds1 = grpc.credentials.createFromMetadataGenerator(function(args, callback) {
  let metadata = new grpc.Metadata();
  metadata.add('macaroon', macaroon1);
  callback(null, metadata);
});
let creds1 = grpc.credentials.combineChannelCredentials(sslCreds1, macaroonCreds1);
let lnd1 = new lnrpc.Lightning('localhost:10001', creds1);
let router1 = new routerrpc.Router('localhost:10001', creds1);
let invoicesrpc1 = new invoicesrpc.Invoices('localhost:10001', creds1);


// LND2

const macaroon2 = fs.readFileSync('/home/rob/app-container/.lnd2/data/chain/bitcoin/regtest/admin.macaroon').toString('hex');
const lndCert2 = fs.readFileSync("/home/rob/app-container/.lnd2/tls.cert");
const sslCreds2 = grpc.credentials.createSsl(lndCert2);
const macaroonCreds2 = grpc.credentials.createFromMetadataGenerator(function(args, callback) {
  let metadata = new grpc.Metadata();
  metadata.add('macaroon', macaroon2);
  callback(null, metadata);
});
let creds2 = grpc.credentials.combineChannelCredentials(sslCreds2, macaroonCreds2);
let lnd2 = new lnrpc.Lightning('localhost:10010', creds2);
let router2 = new routerrpc.Router('localhost:10010', creds2);
let invoicesrpc2 = new invoicesrpc.Invoices('localhost:10010', creds2);


// LND3

const macaroon3 = fs.readFileSync('/home/rob/app-container/.lnd3/data/chain/bitcoin/regtest/admin.macaroon').toString('hex');
const lndCert3 = fs.readFileSync("/home/rob/app-container/.lnd3/tls.cert");
const sslCreds3 = grpc.credentials.createSsl(lndCert3);
const macaroonCreds3 = grpc.credentials.createFromMetadataGenerator(function(args, callback) {
  let metadata = new grpc.Metadata();
  metadata.add('macaroon', macaroon3);
  callback(null, metadata);
});
let creds3 = grpc.credentials.combineChannelCredentials(sslCreds3, macaroonCreds3);
let lnd3 = new lnrpc.Lightning('localhost:10100', creds3);
let router3 = new routerrpc.Router('localhost:10100', creds3);
let invoicesrpc3 = new invoicesrpc.Invoices('localhost:10100', creds3);


/* Auction
 * LND2 is autcioneer
 * LND1 is first bidder
 * LND3 is second bidder
 */

// LND1 (first bidder) sees the auction and asks for an invoice to place the first bid
// LND2 (Auctioneer) creates a normal invoice for the first bid 700.000 SATs

let amt = 700000;

// Get Invoice From LND2
let request = {
  value: amt
};
lnd2.addInvoice(request, async function(err, invoice) {
  if (err)
    return;

  // The payment request in the invoice:
  let paymentRequest = invoice.payment_request
  //console.log(' --- Payment request encoded: ');
  //console.log(paymentRequest);

  // Handing over the request to LND1
  try {
    await checkPayment(lnd1, paymentRequest);
    //console.log(' --- Request accepted!');
    await payInvoice(router1, paymentRequest
    //console.log(' --- Payment done!');
    createHoldInvoice(invoicesrpc1, lnd1, amt, "refund")
  } catch (ex) {
    console.log(ex);
    console.log(' --- ERROR WHILE PROCESS!');
  }

  // LND1 decodes  payment request to check

});

function checkPayment (lnd, paymentRequest) {
  return new Promise((resolve, reject) => {
    let decodePayReqRequest = {
      pay_req: paymentRequest
    };
    lnd.decodePayReq(decodePayReqRequest, function(err, paymentRequestDecoded) {
      if (err)
        return reject(err);
      //console.log(' - Payment request decoded: ');
      //console.log(paymentRequestDecoded);

      if (false) // TODO: Implement conditions
        return reject(new Error(' - Payment does not meet conditions.'));

      // LND1 checks it's channel balance
      lnd.channelBalance({}, function(err, balance) {
        if (err)
          return reject(err);
        //console.log(' - Balance: ');
        //console.log(balance);
        if (balance.local_balance.sat < paymentRequestDecoded.num_satoshis) // TODO: Implement conditions
          return reject(new Error(' - Balance does not meet conditions.'));
        return resolve(paymentRequestDecoded);
      });
    });
  });
}

// Pay Invoice
function payInvoice (router, paymentRequest) {
  return new Promise((resolve, reject) => {
    let requestParameters = {
      payment_request: paymentRequest,
      timeout_seconds: 5
    }
    let call = router.sendPaymentV2(requestParameters);
    call.on('data', function(response) {
      // A response was received from the server.
      //console.log(' - Data: ');
      //console.log(response);
      if (response.status == 'SUCCEEDED')
        resolve(response);
      if (response.status == 'FAILED')
        reject(new Error(' - Payment failed.'));
    });
    call.on('status', function(status) {
      // The current status of the stream.
    });
    call.on('end', function() {
      // The server has closed the stream.
      console.log(' - Payment succeeded!');
      //console.log(response);
    });
  })
}


// Hold invoice

const crypto = require('crypto');

function createHoldInvoice (invoicesrpc, lnd, amount, memo) {
  return new Promise((resolve, reject) => {
    const secret = crypto.randomBytes(32);
    console.log('Generated secrect:  ' + secret.toString('hex'));
    const hash = crypto.createHash('sha256').update(secret).digest();
    console.log('Corresponding hash: ' + hash.toString('hex'));
    request = {
      memo: memo,
      hash: hash,
      value: amount,
      expiry: 3600
    };
    invoicesrpc.AddHoldInvoice(request, function(err, holdInvoice) {
      if (err) {
        return reject(err);
      }
      if (holdInvoice) {
        console.log(holdInvoice);
        var decodePayReqRequest = {
          pay_req: holdInvoice.payment_request
        };
        lnd.decodePayReq(decodePayReqRequest, function(err, response_dec){
          if (err)
            return reject(err);
          if (response_dec)
            return resolve([holdInvoice,secret]);
        });
      }
    });
  });
}
