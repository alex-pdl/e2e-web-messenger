const sessionToken = localStorage.getItem('sessionToken');

if (sessionToken == null){
    localStorage.clear();
    window.location.replace("/login");
}

const params = new URLSearchParams(document.location.search);
const chattingWith = params.get('chatWith')

if (chattingWith === null){
    window.location.replace("/chats");
}

const password = localStorage.getItem('password');
const encryptedPrivateKey = localStorage.getItem('encryptedPrivateKey');
const exportedPublicKey = localStorage.getItem('exportedPublicKey');

import {
    createAESKey,
    decryptRSAKeyFromStorage,
    unwrapImportAesKey,
    encryptMessage,
    decryptMessage
} from './modules/crypto/cryptoUtils.js';

const username = localStorage.getItem('username');

let privateKey = '';
let aesChatKey = '';
let chatId = 0;

const socket = io();

socket.emit('verify_session', sessionToken);

socket.on('unverified', (data) => {
    localStorage.clear();
    window.location.replace("/login");
});

socket.on('verified', (data) => {
    document.getElementById('title').textContent = chattingWith;
    document.body.style.display = 'flex';
});

socket.emit('verify_chat', 
    {
        'requester': username,
        'chatWith': params.get('chatWith'),
    }, sessionToken)

socket.on('initialise_chat', async (data) => {
    const encryptedAesChatKey = data['aesKey']

    const unwrappingAesKey = await createAESKey(password, 'test');
    privateKey = await decryptRSAKeyFromStorage(encryptedPrivateKey, unwrappingAesKey);

    aesChatKey = await unwrapImportAesKey(encryptedAesChatKey, privateKey);

    chatId = data['chatId'];

    const messages = data['messages'];
    const formattedMsgs = await formatDecryptChatMsgs(messages);

    formattedMsgs.forEach(displayMessage)

    scrollDownChats();
});

socket.on('receive_msg', async (msgData) => {
    const sender = msgData['sender'];
    const date = msgData['date'];
    const cipherTxt = msgData['contents'];
    const decryptedContents = await decryptMessage(cipherTxt, aesChatKey);

    const decryptedMsg = {
        'sender': sender,
        'date': date,
        'contents': decryptedContents
    };

    displayMessage(decryptedMsg);

    scrollDownChats();
});

document.addEventListener('click', (event) => {
    if (event.target.id === 'return-btn'){
        window.location.href = '/chats';
    }

    if (event.target.id === 'send-msg-button'){
        sendMessage(document.getElementById('message-input').value);
        document.getElementById('message-input').value = '';
    }
})

document.addEventListener('keypress', (event) => {
    if (event.key === 'Enter'){
        sendMessage(document.getElementById('message-input').value);
        document.getElementById('message-input').value = '';
    }
});

async function sendMessage(content){
    if (content === ''){return}

    const encryptedMessage = await encryptMessage(content, aesChatKey);

    let now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();

    let serverDate = new Date().toUTCString()
    let localDate = serverDate;

    const rawMessage = {
        'sender': username,
        'contents': content,
        'date': localDate
    };

    const cipheredMsg = {
        'chatid': chatId,
        'sender': username,
        'receiver': chattingWith,
        'contents': encryptedMessage,
        'date': serverDate
    };

    displayMessage(rawMessage);
    
    socket.emit('send_message', sessionToken, cipheredMsg);

    scrollDownChats();
}

async function displayMessage(message){
    const msg = document.createElement('div');
    msg.classList.add('message-container');

    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');

    const contents = document.createElement('p');
    contents.innerText = message['contents'];
    contents.classList.add('msg-contents');

    bubble.appendChild(contents);

    const timeStamp = document.createElement('div');
    timeStamp.textContent = message['date'];
    timeStamp.classList.add('timestamp');

    msg.appendChild(bubble);
    msg.appendChild(timeStamp);

    if (message['sender'] === username){
        msg.classList.add('you');
    }
    else {
        msg.classList.add('not-you');
    }

    document.getElementById('chat-messages').appendChild(msg);
}

async function formatDecryptChatMsgs(messages){
    const formattedMsgs = [];

    for (let i = 0; i < messages[0].length; i++){
        const msg_info = messages[0][i];
        const timestamp = msg_info[0];
        const sender = msg_info[1];
        const encryptedContents = messages[1][i];

        const decryptedContents = await decryptMessage(encryptedContents, aesChatKey)

        const message = {
            'sender': sender, 
            'date': timestamp, 
            'contents': decryptedContents
        }

        formattedMsgs.push(message)
    }

    return formattedMsgs;
}

function convertUTCtoLocal(utcTime){
    const localTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    const localTime = new Date().toLocaleString('en-GB', { 
            timeZone: localTimeZone 
        }
    );

    return localTime;
}

function scrollDownChats(){
    const chatContainer = document.getElementById('chat-messages');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}