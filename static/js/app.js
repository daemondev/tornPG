var ws = null;
var URL = 'ws://192.168.3.103:8000/ws';
//var URL = 'ws://localhost:8000/ws';
handlers = {
    'fillTable': fillTable,
    'notifyStatus': notifyStatus,
    'listFiles': listFiles,
    'notifyFromDB': notifyFromDB
};

function listFiles (message) {
    tblFilesBody = document.getElementById('tblFilesBody');
    tr = '';
    for (var i = 0; i < message.total; i++) {
        tr = tr + '<tr><td>' + (i+1) + '</td><td>'  + message.name[i]  + '</td><td>' + message.size[i] + '</td><td>' + message.date[i]  + '</td></tr>';
    }
    tblFilesBody.innerHTML = tr;
}

function notifyFromDB (message) {
    alert('receive database notification: ' + message);
}

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
    dels = document.getElemenstByClassName('delete');
    for (i = 0; i < dels.length; i++) {
        alert('data');
        dels[i].onclick = deleteItem;
    }

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
    if (event == 'multi') {
        for (var i = 0; i < data.length; i++) {
            handlers[data[i]['event']](data[i]['data']);
        }
    }else{
        handlers[event](data);
    }
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
    if (userData.id != "") {
        send('updateIten', userData);
    }
}

function btnListFilesOnClick(e){
    e.preventDefault();
    send('listFiles',{});
    toggleDivs('divFiles');
}

function btnListUsersOnClick(e){
    e.preventDefault();
    send('listUsers', {});
    toggleDivs('divUsers');
}

function toggleDivs(currentDiv){
    ddc = document.getElementById('divDataContainners');
    divs = ddc.getElementsByTagName('div');
    for (var i = 0; i < divs.length; i++) {
        if (divs[i].id != currentDiv) {
            divs[i].style.display = 'none';
        }
    }
    document.getElementById(currentDiv).style.display = 'block';
}

function prepare() {
    document.getElementById('btnListFiles').onclick = btnListFilesOnClick;
    document.getElementById('btnListUsers').onclick = btnListUsersOnClick;
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
