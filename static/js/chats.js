const chatsContainer = document.getElementById("chats");
const errorMsgDiv = document.getElementById('errorMsg');
const chatBtns = document.getElementsByClassName('chat-btn');
const url = window.location.href;
const user = url.substring(url.lastIndexOf('/')+1);

const socket = io();

socket.emit('store_sid', user);

function addEmptyMessage(){
    const emptyMsgP1 = document.createElement('p');
    const emptyMsgP2 = document.createElement('p');

    emptyMsgP1.textContent = 'No chats yet! 👋';
    emptyMsgP2.textContent = 'Start a conversation by adding a user below.';

    chatsContainer.append(emptyMsgP1);
    chatsContainer.append(emptyMsgP2);
}

if (chatsContainer.querySelector('ul').childElementCount == 0){
    addEmptyMessage();
}

socket.on('add_chat_btn', (name) => {
    /* Remove empty message text*/
    chatsContainer.querySelectorAll('p').forEach((element) => {
        element.remove();
    });

    errorMsgDiv.innerHTML = '';
    document.getElementById('addTextInput').blur();

    let chat = `<li><button class="chat-btn" onclick=redirectToChat('${name}')>${name}</button></li>`;

    chatsContainer.querySelector('ul').innerHTML += chat;
});

socket.on('display_error', (error) => {
    errorMsgDiv.innerHTML = `<p>${error}</p>`;
});

document.getElementById('addUserSubmitBtn').addEventListener('click', () => {
    const userInput = document.getElementById('addTextInput');
    
    if (userInput.value === ''){
        return
    };

    let inputName = userInput.value;

    socket.emit('add_chat', inputName);

    userInput.value = '';
});

function redirectToChat(name){
    window.location.href = `/message?selected_name=${name}`
}

window.addEventListener('beforeunload', () => {
    socket.emit('remove_sid', user);
    });