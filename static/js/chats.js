import {
    importPublicKeyFromStorage,
    generateRandomAesKey,
    wrapExportAESKey
} from './modules/crypto/cryptoUtils.js';

const sessionToken = localStorage.getItem('sessionToken');

if (sessionToken == null){
    localStorage.clear();
    window.location.replace("/login");
}

const title = document.getElementById('title');
const logoutBtn = document.getElementById('logoutBtn');
const chatsContainer = document.getElementById("chats");
const addUser = document.getElementById('addUser');

const errorMsgDiv = document.getElementById('errorMsg');
const chatBtns = document.getElementsByClassName('chat-btn');
const addUserToChatBtn = document.getElementById('addUserSubmitBtn');

const username = localStorage.getItem('username');
const publicKey = await importPublicKeyFromStorage(localStorage.getItem('exportedPublicKey'));

const socket = io();

// User auth & page load
socket.emit('verify_session', sessionToken);

socket.on('unverified', (data) => {
    localStorage.clear();
    window.location.replace("/login");
});

socket.on('verified', (usr) => {
    title.textContent = `Welcome ${usr}!`;

    title.style.display = 'block';
    logoutBtn.style.display = 'block';
    chatsContainer.style.display = 'block';
    addUser.style.display = 'block';

    socket.emit('display_chats', sessionToken);
});

// Page functionality
if (chatsContainer.querySelector('ul').childElementCount == 0){
    const emptyMsgP1 = document.createElement('p');
    const emptyMsgP2 = document.createElement('p');

    emptyMsgP1.textContent = 'No chats yet! 👋';
    emptyMsgP2.textContent = 'Start a conversation by adding a user below.';

    chatsContainer.append(emptyMsgP1, emptyMsgP2);
}

document.addEventListener('click', (event) => {
    if (event.target.className === 'chat-btn'){
        const name = event.target.textContent;
        window.location.href = '/messages?chatWith=' + encodeURIComponent(name);
    };

    if (event.target.id === 'addUserSubmitBtn'){
        const userInput = document.getElementById('addTextInput');
        const inputName = userInput.value.trim()
    
        if (inputName === ''){return};

        socket.emit('is_valid_chat_creation_request', sessionToken, inputName);

        userInput.value = '';
    }

    if (event.target.id === 'logoutBtn'){
        localStorage.clear();
        window.location.replace("/login");
    }
});

socket.on('generate_chat', async (data) => {
    const user2 = data['receiver'];
    const user2PublicKey = await importPublicKeyFromStorage(data['receiver_public_key']);

    const messageEncryptionKey = await generateRandomAesKey();

    const user1AesKey = await wrapExportAESKey(
        messageEncryptionKey, 
        publicKey
    );

    const user2AesKey = await wrapExportAESKey(
        messageEncryptionKey, 
        user2PublicKey
    );

    const chatData = {
        'creator_token': sessionToken,
        'user1': username,
        'user2': user2,
        'user1AesKey': user1AesKey,
        'user2AesKey': user2AesKey
    };
    
    socket.emit('create_chat', chatData)
});

socket.on('add_chat_btn', (name) => {
    chatsContainer.querySelectorAll('p').forEach((elmt) => {elmt.remove();});

    let chatBtn = `<li><button class="chat-btn">${name}</button></li>`;
    chatsContainer.querySelector('ul').innerHTML += chatBtn;

    errorMsgDiv.innerHTML = '';
    document.getElementById('addTextInput').blur();
});

socket.on('display_error', (error) => {
    errorMsgDiv.innerHTML = `<p>${error}</p>`;
});

socket.on('new_chat_msg', (name) => {
    const newChatMsg = document.createElement("div");
    newChatMsg.textContent = `${name} has started a new chat with you.`;
    newChatMsg.id = 'new-chat-msg';
    document.body.appendChild(newChatMsg);

    document.getElementById('new-chat-msg').addEventListener('animationend', () => {
    document.getElementById("new-chat-msg").remove();});
});
  
// On page unload
window.addEventListener('beforeunload', () => {
    socket.emit('remove_sid', username);
});