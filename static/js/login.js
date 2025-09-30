const socket = io();

const errorMsg = document.getElementById('errorMsg');
const errorMsgP = errorMsg.querySelector('p');

let username = '';
let password = '';

import {
    hashPassword
} from './modules/crypto/cryptoUtils.js';

submitBtn.addEventListener('click', async () => {
    username = document.getElementById('username').value;
    password = document.getElementById('password').value;

    const hashedPassword = await hashPassword(password);

    socket.emit('login', username, hashedPassword);
})

socket.on('display_error', (error) => {
    errorMsgP.textContent = error;

    username = '';
    password = '';
});

socket.on('success', (data) => {
    localStorage.setItem("username", username);
    localStorage.setItem("password", password);

    localStorage.setItem("exportedPublicKey", data['publicKey']);
    localStorage.setItem("encryptedPrivateKey", data['privateKey']);
    localStorage.setItem("sessionToken", data['sessionToken']);

    window.location.replace("/chats");
})