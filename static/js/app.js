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
        tr = tr +'<tr><td>' + user.id + '</td><td>' + user.nombre + '</td><td>' + user.direccion + '</td><td>' + user.telefono + '</td><td>' + user.usuario + '</td><td>' + '<a link="" href="#" class="edit" onclick="editItem(event)">Edit</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href="#" class="delete" onclick="deleteItem(event)">Delete</a>'  + '</td></tr>';
    });
    tBody.innerHTML = tr;
//--------------------------------------------------
//     dels = document.getElementsByClassName('delete');
//     for (i = 0; i < dels.length; i++) {
//         alert('data');
//         dels[i].onclick = deleteItem;
//     }
//--------------------------------------------------

}

function collectData(){
    id = document.getElementById('id').value;
    user = document.getElementById('User Name:').value;
    address = document.getElementById('Address:').value;
    phone = document.getElementById('Phone:').value;
    email = document.getElementById('Email:').value;

    data = {'id': id, "user": user, 'address': address, 'phone': phone, 'email': email};
    return data;
}

function sendMessage() {
    userData = collectData();
    send('saveUser', userData);
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

function btnLoadDataOnClick(){
    loadData();
}

function send(event, data){
    ws.send(JSON.stringify({'event': event, 'data': data}));
}

function loadData(){
    send('loadPandas', {});
}

function deleteItem(e){
    e.preventDefault();
    self = e.target;
    id = self.parentNode.parentNode.cells[0].innerHTML;
    send('deleteItem', {'id': id});
    //alert('deleting value with event ' + self.parentNode.parentNode.cells[0].innerHTML);
}

function editItem (e) {
    e.preventDefault();
    self = e.target;
    cells = self.parentNode.parentNode.cells;

    document.getElementById('User Name:').value = cells[1].innerHTML;
    document.getElementById('id').value = cells[0].innerHTML;
    document.getElementById('Address:').value = cells[2].innerHTML;
    document.getElementById('Phone:').value = cells[3].innerHTML;
    document.getElementById('Email:').value = cells[4].innerHTML;
}

function btnUpdateOnClick(e){
    e.preventDefault();
    userData = collectData();
    send('updateIten', userData);
}

function btnListFilesOnClick(e){
    send('listFiles',{});
}

function prepare() {
    document.getElementById('btnListFiles').onclick = btnListFilesOnClick;
    document.getElementById('btnUpdate').onclick = btnUpdateOnClick;
    document.getElementById('btnSubmit').onclick = btnSubmitOnClick;
    document.getElementById('btnLoadData').onclick = btnLoadDataOnClick;
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
