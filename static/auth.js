let isRegister = false;

function switchMode() {
    isRegister = !isRegister;
    document.getElementById("title").innerText = isRegister ? "Register" : "Login";
    document.getElementById("submitBtn").innerText = isRegister ? "Create" : "Login";
    document.getElementById("authForm").action = isRegister ? "/register" : "/login";
    document.getElementById("modeBtn").innerText = isRegister ? "Back to Login" : "Register";
}

function checkStrength(pwd) {
    let s = document.getElementById("strengthText");
    if (pwd.length < 4) s.innerText = "Weak";
    else if (pwd.length < 8) s.innerText = "Medium";
    else s.innerText = "Strong";
}
