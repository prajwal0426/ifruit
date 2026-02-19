const toggle = document.getElementById("toggle");
const authBox = document.getElementById("authBox");
const spotlight = document.getElementById("spotlight");
const form = document.getElementById("authForm");
const title = document.getElementById("title");
const strengthText = document.getElementById("strengthText");

let isOn = false;
let isRegister = false;

/* Toggle popup + spotlight */
toggle.onclick = () => {
    isOn = !isOn;
    toggle.classList.toggle("on");
    authBox.classList.toggle("show");

    if (isOn) {
        spotlight.style.opacity = "1";   // 🔆 show light
    } else {
        spotlight.style.opacity = "0";   // 🌑 hide light
    }
};

/* Switch login/register */
function switchMode() {
    isRegister = !isRegister;

    if (isRegister) {
        title.innerText = "Register";
        form.action = "/register";
    } else {
        title.innerText = "Login";
        form.action = "/login";
    }
}

/* Password strength */
function checkStrength(pwd) {
    if (pwd.length < 4) {
        strengthText.innerText = "Weak";
        strengthText.style.color = "red";
    } else if (pwd.length < 8) {
        strengthText.innerText = "Medium";
        strengthText.style.color = "orange";
    } else {
        strengthText.innerText = "Strong";
        strengthText.style.color = "lightgreen";
    }
}
