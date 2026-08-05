
# e2e-web-messenger
A self-hostable, end-to-end encrypted real-time messaging web application built with Python. Utilising WebSocket-based communication and a responsive web interface. Based off of my previous project, [Senderr](https://github.com/alex-pdl/senderr).


![preview](/readme-imgs/chat_preview.gif)

You can check out my instance [here](https://e2e-web-messenger.site)! <small>Note: An account is required to add and message people.</small>
## Tech Stack

- Backend: Python, Flask, [Socket.IO](https://socket.io/) (for WebSockets) 
- Frontend: HTML, CSS, JavaScript, [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API) (for encryption)
- Database: SQLite

## How to get started (macos/linux)
### Download
```
git clone https://github.com/alex-pdl/e2e-web-messenger.git
cd e2e-web-messenger/
```
### Running Directly 
```
pip install -r requirements.txt
python3 app.py
```
### Running in docker container
```
docker build -t e2e-web-messenger .
docker run -d --name=e2e-web-messenger --restart=always -p 5000:5000 e2e-web-messenger
```

## Brief Overview (how it works)
Each chat has a unique AES key used to encrypt message content. When a chat is created, the sender generates this key in the browser and wraps (encrypts) it separately with the public key of each participant. It can only be unwrapped by the private key of each participant (which leaves the client). The server stores only these wrapped copies, so it can never decrypt a message. On every visit to a chat, both clients fetch their wrapped copy from the server and unwrap it locally to encrypt/decrypt messages in the browser.
![encryption system diagram](/readme-imgs/encryption-diagram.png)
<small>Please do not use this software for any highly sensitive communication. It has not been audited by security professionals.</small>

## Important Considerations

Here are some of the project's limitations:

- Metadata is visible to the server such as: which users are talking to each other and the times of their messages.
  - only the message contents are fully encrypted.

- There is no feature to verify the public key of the person you're chatting with, like signal's [safety numbers](https://support.signal.org/hc/en-us/articles/360007060632-What-is-a-safety-number-and-why-do-I-see-that-it-changed).

- No method of key rotation; each chat uses one AES key for its lifetime rather than changing keys per-message or per-session.

These are features I am considering adding in the future!
