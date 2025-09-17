const username = localStorage.getItem('username');
const sessionToken = localStorage.getItem('sessionToken');

const socket = io();

socket.emit('verify_session', sessionToken);

socket.on('unverified', (data) => {
    window.location.replace("/login");
});

socket.on('verified', (data) => {
    
});
