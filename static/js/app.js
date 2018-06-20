var ws = null;
var URL = 'ws://localhost:8000/ws';
handlers = {
    'fillTable': fillTable,
    'notifyStatus': notifyStatus
};

function notifyStatus(message) {
    document.getElementById('status').innerHTML = message;
}

function fillTable(data) {
    tBody = document.getElementById('tblBaseBody');
    tr = '';
    data.map(function(user){
        tr = tr +'<tr><td>' + user.nombre + '</td><td>' + user.direccion + '</td><td>' + user.telefono + '</td><td>' + user.usuario + '</td></tr>';
    });
    tBody.innerHTML = tr;
}

function sendMessage() {
    user = document.getElementById('User Name:').value;
    address = document.getElementById('Address:').value;
    phone = document.getElementById('Phone:').value;
    email = document.getElementById('Email:').value;

    data = {'event':'saveUser', 'data': {"user": user, 'address': address, 'phone': phone, 'email': email}};
    ws.send(JSON.stringify(data));
}

function onOpen(){
    notifyStatus('Connected!!!');
}

function onMessage(r) {
    raw = eval('(' + r.data + ')');
    event = raw['event'];
    data = raw.data;
    handlers[event](data);
}

function btnSubmitOnClick(e) {
    e.preventDefault();
    sendMessage();
}

function prepare() {
    document.getElementById('btnSubmit').onclick = btnSubmitOnClick;
    document.getElementById('User Name:').value = 'Richar Muñico Samaniego';
    document.getElementById('Address:').value = 'San Juan de Miraflores';
    document.getElementById('Phone:').value = '982929041';
    document.getElementById('Email:').value = 'granlinux@gmail.com';
}

function init(){
    ws = new WebSocket(URL);
    ws.onopen = onOpen;
    ws.onmessage = onMessage;
    prepare();
}

window.onload = init;
