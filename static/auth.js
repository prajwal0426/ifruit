const toggle = document.getElementById("toggle"); 
const authBox = document.getElementById("authBox");
const spotlight = document.getElementById("spotlight");
const form = document.getElementById("authForm");
const title = document.getElementById("title");
const submitBtn = document.getElementById("submitBtn");
const modeBtn = document.getElementById("modeBtn");
const strengthText = document.getElementById("strengthText");
const avatarBox = document.getElementById("avatarBox");
const avatarInput = document.getElementById("avatarInput");

/* ============================= */
/* ✅ ADDED: selected avatar var */
/* ============================= */
let selectedAvatar = null;

/* ============================= */
/* ✅ ADDED: username input ref  */
/* ============================= */
const usernameInput = document.querySelector('input[name="username"]');

function selectAvatar(path) {
  avatarInput.value = path;

  /* ============================= */
  /* ✅ ADDED: store avatar choice */
  /* ============================= */
  selectedAvatar = path;
  checkFormReady();
}

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
    avatarBox.style.display = "block"; // SHOW AVATARS
  } else {
    title.innerText = "Login";
    submitBtn.innerText = "Login";
    form.action = "/login";
    modeBtn.innerText = "Register";
    avatarBox.style.display = "none"; // HIDE AVATARS
  }

  /* ============================= */
  /* ✅ ADDED: reset button state  */
  /* ============================= */
  checkFormReady();
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

  /* ============================= */
  /* ✅ ADDED: re-check form state */
  /* ============================= */
  checkFormReady();
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
/* ✅ ADDED: form readiness check */
/* ============================= */
function checkFormReady() {
  if (
    isRegister &&
    usernameInput.value.trim() !== "" &&
    passwordInput.value.trim() !== "" &&
    selectedAvatar !== null
  ) {
    submitBtn.disabled = false;
    submitBtn.classList.add("active");
  } else if (!isRegister) {
    submitBtn.disabled = false;
    submitBtn.classList.add("active");
  } else {
    submitBtn.disabled = true;
    submitBtn.classList.remove("active");
  }
}

/* ============================= */
/* ✅ ADDED: input listeners     */
/* ============================= */
usernameInput.addEventListener("input", checkFormReady);

/* ============================= */
/* ✅ ADDED: 👁️ Password toggle */
/* ============================= */

const passwordInput = document.getElementById("passwordInput");
const eyeToggle = document.getElementById("eyeToggle");

passwordInput.addEventListener("input", checkFormReady);

function togglePassword() {
  
  eyeToggle.classList.add("animate");

  setTimeout(() => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      eyeToggle.classList.remove("closed");
      eyeToggle.classList.add("open");
    } else {
      passwordInput.type = "password";
      eyeToggle.classList.remove("open");
      eyeToggle.classList.add("closed");
    }

    
    eyeToggle.classList.remove("animate");
  }, 150);
}