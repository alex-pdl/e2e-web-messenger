import {
    genRsaKey, 
    createAESKey, 
    encryptKeyForStorage, 
    decryptKeyFromStorage
} from './modules/crypto/cryptoUtils.js';

const usernameInputBox = document.getElementById('usernameBox');
const passwordInputBox = document.getElementById('passwordBox');
const errorMsg = document.getElementById('errorMsg');
const errorMsgP = errorMsg.querySelectorAll('p');

let isValidUsername = false;
let isValidPassword = false;

const lightGreen = 'rgb(39, 190, 51)';
const darkGreen = 'rgba(32, 151, 42, 1)';
const lightRed = 'rgb(253, 51, 51)';
const darkRed = 'rgba(176, 35, 35, 1)';

['focus', 'blur', 'input'].forEach((e) => {
    usernameInputBox.querySelector('input').addEventListener(e, usernameInputFunctionality);
    passwordInputBox.querySelector('input').addEventListener(e, passwordInputBoxFunctionality);
});

function usernameInputFunctionality(event){
    switch(event.type) {
        case 'focus':
            const usernameCriteria = document.createElement("ul");
            usernameCriteria.classList.add('criteria');
            
            const lengthCriteria = document.createElement("li");
            lengthCriteria.textContent = "Minimum 4 characters";
            lengthCriteria.id = "lengthCriteria";

            const charCriteria = document.createElement("li");
            charCriteria.textContent = "No special characters or spaces";
            charCriteria.id = "charCriteria";

            usernameCriteria.append(lengthCriteria, charCriteria);

            usernameInputBox.appendChild(usernameCriteria);
            break;
        case 'blur':
            usernameInputBox.querySelector('ul').remove();
            return;
    }

    const inputtedUsername = event.target.value;
    const usernameInput = document.getElementById('username');

    const lenCriteria = document.getElementById('lengthCriteria');
    const charCriteria = document.getElementById('charCriteria');

    const isLongEnough = inputtedUsername.length >= 4;
    const hasSpecialChars = /[^A-Za-z0-9]/.test(inputtedUsername);

    lenCriteria.style.color = isLongEnough ? lightGreen : lightRed;
    charCriteria.style.color = !hasSpecialChars ? lightGreen : lightRed;

    isValidUsername = isLongEnough && !hasSpecialChars;
    usernameInput.style.borderColor = isValidUsername ? darkGreen : darkRed;
}

function passwordInputBoxFunctionality(event){
    switch(event.type) {
        case 'focus':
            const usernameCriteria = document.createElement("ul");
            usernameCriteria.classList.add('criteria');
            
            const lengthCriteria = document.createElement("li");
            lengthCriteria.textContent = "Minimum 8 characters";
            lengthCriteria.id = "lengthCriteria";

            const upperCaseCriteria = document.createElement("li");
            upperCaseCriteria.textContent = "At least one uppercase letter";
            upperCaseCriteria.id = "upperCaseCriteria";

            const lowerCaseCriteria = document.createElement("li");
            lowerCaseCriteria.textContent = "At least one lowercase letter";
            lowerCaseCriteria.id = "lowerCaseCriteria";

            const specialCharCriteria = document.createElement("li");
            specialCharCriteria.textContent = "At least one special character";
            specialCharCriteria.id = "specialCharCriteria";

            usernameCriteria.append(lengthCriteria, upperCaseCriteria, lowerCaseCriteria, specialCharCriteria);

            passwordInputBox.appendChild(usernameCriteria);
            break;
        case 'blur':
            passwordInputBox.querySelector('ul').remove();
            return;
    }

    const inputtedPassword = event.target.value;
    const passwordInput = document.getElementById('password');

    const isLongEnough = inputtedPassword.length >= 8;
    const hasAUpperCaseChar = !(inputtedPassword === inputtedPassword.toLowerCase());
    const hasALowerCaseChar = !(inputtedPassword === inputtedPassword.toUpperCase());
    const hasASpecialChar = /[^A-Za-z0-9]/.test(inputtedPassword);

    lengthCriteria.style.color = isLongEnough ? lightGreen : lightRed;
    upperCaseCriteria.style.color = hasAUpperCaseChar ? lightGreen : lightRed;
    lowerCaseCriteria.style.color = hasALowerCaseChar ? lightGreen : lightRed;
    specialCharCriteria.style.color = hasASpecialChar ? lightGreen : lightRed;
    
    isValidPassword = isLongEnough && hasAUpperCaseChar && hasALowerCaseChar && hasASpecialChar;
    passwordInput.style.borderColor = isValidPassword ? darkGreen : darkRed;
}