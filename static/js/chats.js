const chatsContainer = document.getElementById("chats");

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