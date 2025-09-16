const title = document.getElementById('title');
const logoutBtn = document.getElementById('logoutBtn');
const chatsContainer = document.getElementById("chats");
const addUser = document.getElementById('addUser');

const errorMsgDiv = document.getElementById('errorMsg');
const chatBtns = document.getElementsByClassName('chat-btn');
const addUserToChatBtn = document.getElementById('addUserSubmitBtn');

const url = window.location.href;
const user = url.substring(url.lastIndexOf('/')+1);

const username = localStorage.getItem('username');
const sessionToken = localStorage.getItem('sessionToken');

const socket = io();

function addChatButton(name){
    /* Remove empty message text*/
    
};

// User auth & page load
socket.emit('verify_session', 
    {
        'username': username, 
        'sessionToken': sessionToken
    }
);

socket.on('unverified', (data) => {
    window.location.replace("/login");
});

socket.on('verified', (data) => {
    title.textContent = `Welcome ${username}!`;

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
})

// Button functionality
document.addEventListener('click', (event) => {
    if (event.target.className === 'chat-btn'){
        const name = event.target.textContent;
        window.location.href = '/messages?chatWith=' + encodeURIComponent(name);
    };

    if (event.target.id === 'addUserSubmitBtn'){
        const userInput = document.getElementById('addTextInput');
        const inputName = userInput.value.trim()
    
        if (inputName === ''){return};

        socket.emit('add_chat', sessionToken, inputName);

        userInput.value = '';
    }
});
  
// On page unload
window.addEventListener('beforeunload', () => {
    socket.emit('remove_sid', user);
});