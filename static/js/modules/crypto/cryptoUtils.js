function concatenateBuffers(buffer1, buffer2){
    const newBuffer = new Uint8Array(buffer1.byteLength + buffer2.byteLength);

    newBuffer.set(new Uint8Array(buffer1), 0);
    newBuffer.set(new Uint8Array(buffer2), buffer1.byteLength);
    
    return newBuffer;
}

function stringToBuffer(str){
    const encoder = new TextEncoder();
    const buffer = encoder.encode(str);

    return new Uint8Array(buffer);
}

function ab2str(buf) {
    return String.fromCharCode.apply(null, new Uint8Array(buf));
}

function str2ab(str) {
    const buf = new ArrayBuffer(str.length);
    const bufView = new Uint8Array(buf);
    for (let i = 0, strLen = str.length; i < strLen; i++) {
        bufView[i] = str.charCodeAt(i);
    }
    return buf;
}

export async function genRsaKey() {
    const keyPair = await crypto.subtle.generateKey(
        {
            'name': "RSA-OAEP",
            'modulusLength': 2048,
            'publicExponent': new Uint8Array([1, 0, 1]),
            'hash': 'SHA-256'
        },
        true,
        ['encrypt', 'decrypt']
    );

    return keyPair
}

export async function createAESKey(password, salt){
    const importedKey = await crypto.subtle.importKey(
        'raw',
        stringToBuffer(password),
        {'name': 'PBKDF2'},
        false,
        ['deriveKey']
    )

    const derivedAesKey = await crypto.subtle.deriveKey(
        {
            'name': 'PBKDF2',
            'hash': 'SHA-256',
            'salt': stringToBuffer(salt),
            'iterations': 10000
        },
        importedKey,
        {'name': 'AES-GCM', 'length': 256},
        true,
        ['wrapKey', 'unwrapKey']
    )

    return derivedAesKey;
}

export async function encryptKeyForStorage(privateKey, wrappingKey){
    const iv = crypto.getRandomValues(new Uint8Array(96));
    const wrappedPrivateKey = await crypto.subtle.wrapKey(
        'pkcs8',
        privateKey, 
        wrappingKey, 
        {'name': 'AES-GCM', 'iv': iv}
    );

    // Wrapped key is prepended with its intialisation vector

    return btoa(ab2str(concatenateBuffers(wrappedPrivateKey, iv)));
}

export async function decryptKeyFromStorage(importedKey, unwrapKey){
    const importedKeyAsBuffer = str2ab(atob(importedKey));
    const len = importedKeyAsBuffer.byteLength

    const wrappedKey = importedKeyAsBuffer.slice(0, len - 96);
    const iv = importedKeyAsBuffer.slice(len-96);
    
    const decryptedKey = await crypto.subtle.unwrapKey(
        'pkcs8',
        wrappedKey,
        unwrapKey,
        {'name': 'AES-GCM', 'iv': iv},
        {'name': 'RSA-OAEP', 'hash': 'SHA-256'},
        [true],
        ['decrypt']
    );
    
    return decryptedKey;
}