// Story
var tx
addText('Seller S creates an auction')
addText('Seller S creates a “virtual” funding TX (VFTX_S1) which he could post to the blockchain at any time')
tx = {
  type: "vf",
  id: "S 1",
  comment: "Virtual Funding",
  location: "S",
  state: "off-chain",
  inputs: [
    {
      value: 0.01,
      txid: "f S",
      vout: 0,
      scripts: [
        [
          "S ✓"
        ]
      ]
    }
  ],
  outputs: [
    {
      value: 0.01,
      vout: 0,
      scripts: [
        [
          "S ⬜"
        ]
      ]
    }
  ]
}
generateTXTable(tx);
addText('Seller S announces Unspent TX Output UTXO VFTX_S1 which corresponds to VFTX _S1')

addText('Bidder B gets inital commitment TX from S.')

tx = {
  type: "c",
  id: "SB 1",
  comment: "1st Commitment TX",
  location: "B",
  state: "off-chain",
  inputs: [
    {
      value: 2,
      txid: "f B",
      vout: 0,
      scripts: [
        [
          "B ✓",
          "S ⬜"
        ]
      ]
    }
  ],
  outputs: [
    {
      value: 2,
      vout: 0,
      scripts: [
        [
          "B ⬜",
          "⏳ 2 weeks"
        ],
        [
          "S ⬜",
          "🔒 KeyB1 required"
        ]
      ]
    }
  ]
}
generateTXTable(tx);
