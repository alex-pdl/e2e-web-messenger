const errorMsg = document.getElementById('errorMsg');
const errorMsgP = errorMsg.querySelectorAll('p');

function redirectMessage(msg, count){
    msg.style.backgroundColor = 'rgb(39, 190, 51)';
    msg.textContent = "You have successfully registered an account."
                    + ", you will be redirected in: " + count;
}

if (errorMsgP.length !== 0){
    const msg = errorMsgP[0];

    if (msg.textContent == "Success"){
        let count = 3;
        redirectMessage(msg, count);
        
        setInterval(() => {
            count--;
            redirectMessage(msg, count);

            if (count === 0){
                window.location.href = '/chats';
            }
        }, 1000)
    }
}