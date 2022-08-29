function generateTXTable(tx) {
  var table = document.createElement("table");
  var tblBody = document.createElement("tbody");

  // Info row
  let row = table.insertRow();
  row.style.fontWeight = 'bold';;
  // ID
  let cell = row.insertCell();
  let text = document.createTextNode(tx.type + ' ' + tx.id);
  cell.appendChild(text);
  // comment
  cell = row.insertCell();
  text = document.createTextNode(tx.comment);
  cell.appendChild(text);
  // Location
  cell = row.insertCell();
  text = document.createTextNode("@" + tx.location);
  cell.appendChild(text);
  // state
  cell = row.insertCell();
  text = document.createTextNode(tx.state);
  cell.appendChild(text);

  // Inputs
  row = table.insertRow();
  // ID
  cell = row.insertCell();
  text = document.createTextNode("Inputs");
  cell.appendChild(text);
  cell.style.fontWeight = 'bold';
  for (let input of tx.inputs) {
    row = table.insertRow();
    // ID
    cell = row.insertCell();
    text = document.createTextNode(input.vout + '. output of ' + input.txid);
    cell.appendChild(text);
    // Value
    cell = row.insertCell();
    text = document.createTextNode(input.value + ' BTC');
    cell.appendChild(text);
    // Scripts
    row = table.insertRow();
    for (let script of input.scripts) {
      cell = row.insertCell();
      text = document.createTextNode(script.join('\n'));
      cell.appendChild(text);
      cell.style.border = '1px solid white'
    }
  }

  // Outputs
  row = table.insertRow();
  // ID
  cell = row.insertCell();
  text = document.createTextNode("Outputs");
  cell.appendChild(text);
  cell.style.fontWeight = 'bold';
  for (let input of tx.outputs) {
    row = table.insertRow();
    // ID
    cell = row.insertCell();
    text = document.createTextNode(input.vout + '. output of ' + tx.id);
    cell.appendChild(text);
    // Value
    cell = row.insertCell();
    text = document.createTextNode(input.value + ' BTC');
    cell.appendChild(text);
    // Scripts
    row = table.insertRow();
    for (let script of input.scripts) {
      cell = row.insertCell();
      text = document.createTextNode(script.join('\n'));
      cell.appendChild(text);
      cell.style.border = '1px solid white'
    }
  }

  table.appendChild(tblBody);
  document.body.appendChild(table);
}


var counter = 1;
function addText(text) {
  var p = document.createElement("p");
  p.style.padding = '0.3em';
  var newtext = document.createTextNode(counter + ".  " + text);
  counter++;
  p.appendChild(newtext);
  document.body.appendChild(p);
}
