const toggle = document.getElementById("toggle");
const authBox = document.getElementById("authBox");
const spotlight = document.getElementById("spotlight");
const form = document.getElementById("authForm");
const title = document.getElementById("title");
const submitBtn = document.getElementById("submitBtn");
const modeBtn = document.getElementById("modeBtn");
const strengthText = document.getElementById("strengthText");

let isOn = false;
let isRegister = false;

/* 🔘 Toggle popup + spotlight */
toggle.onclick = () => {
  isOn = !isOn;
  toggle.classList.toggle("on");
  authBox.classList.toggle("show");
  spotlight.classList.toggle("active", isOn);
};

/* 🔁 Switch Login ↔ Register */
function switchMode() {
  isRegister = !isRegister;

  if (isRegister) {
    title.innerText = "Register";
    submitBtn.innerText = "Create Account";
    form.action = "/register";
    modeBtn.innerText = "Back to Login";
  } else {
    title.innerText = "Login";
    submitBtn.innerText = "Login";
    form.action = "/login";
    modeBtn.innerText = "Register";
  }
}

/* 🔐 Password strength */
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

/* ❌ Auto OFF on error */
const error = document.querySelector(".error");
if (error) {
  spotlight.classList.remove("active");
  toggle.classList.remove("on");
  authBox.classList.remove("show");
  isOn = false;
}

/* ============================= */
/* ✅ ADDED: 👁️ Password toggle */
/* ============================= */

const passwordInput = document.getElementById("passwordInput");
const eyeToggle = document.getElementById("eyeToggle");

// default state
eyeToggle.classList.add("closed");

function togglePassword() {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeToggle.classList.remove("closed");
    eyeToggle.classList.add("open");
  } else {
    passwordInput.type = "password";
    eyeToggle.classList.remove("open");
    eyeToggle.classList.add("closed");
  }
}