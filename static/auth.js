/*  ELEMENT REFERENCES           */

const authBox = document.getElementById("authBox");

const form = document.getElementById("authForm");
const title = document.getElementById("title");
const submitBtn = document.getElementById("submitBtn");
const modeBtn = document.getElementById("modeBtn");
const strengthText = document.getElementById("strengthText");
const avatarBox = document.getElementById("avatarBox");
const avatarInput = document.getElementById("avatarInput");
const usernameInput = document.querySelector('input[name="username"]');
const passwordInput = document.getElementById("passwordInput");
const eyeToggle = document.getElementById("eyeToggle");


/*  LAMP CLICK (NEW)             */

const lamp = document.querySelector(".lamp-label");

if (lamp) {
  lamp.addEventListener("click", () => {
    authBox.classList.toggle("show");
  });
}


/*  ADDED: selected avatar var   */

let selectedAvatar = null;

/*  SELECT AVATAR                */


function selectAvatar(path) {
  avatarInput.value = path;


  selectedAvatar = path;
  checkFormReady();
}


let isRegister = false;



/*  SWITCH LOGIN ↔ REGISTER      */

function switchMode() {

  isRegister = !isRegister;

  if (isRegister) {
    title.innerText = "Register";
    submitBtn.innerText = "Create Account";
    form.action = "/register";
    modeBtn.innerText = "Back to Login";

    if (avatarBox) {
      avatarBox.style.display = "block";
    }

  } else {

    title.innerText = "Login";
    submitBtn.innerText = "Login";
    form.action = "/login";
    modeBtn.innerText = "Register";

    if (avatarBox) {
      avatarBox.style.display = "none";
    }
  }


  checkFormReady();
}


/*  PASSWORD STRENGTH            */

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


  checkFormReady();
}


/*  FORM READY CHECK             */

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


/*  INPUT LISTENERS              */


if (usernameInput) {
  usernameInput.addEventListener("input", checkFormReady);
}

if (passwordInput) {
  passwordInput.addEventListener("input", checkFormReady);
}


/*  PASSWORD EYE TOGGLE          */


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


/*  REGISTER VALIDATION          */


const registerForm = document.querySelector("form[action='/register/save']");
const avatarRadios = document.querySelectorAll("input[name='avatar']");
const createBtn = document.querySelector(".login-btn");

if (registerForm) {

  createBtn.disabled = true;
  createBtn.style.opacity = "0.5";

  function checkRegisterReady() {

    const username = registerForm.querySelector("input[name='username']").value.trim();
    const password = registerForm.querySelector("input[name='password']").value.trim();
    const avatarSelected = [...avatarRadios].some(r => r.checked);

    if (username && password && avatarSelected) {

      createBtn.disabled = false;
      createBtn.style.opacity = "1";

    } else {

      createBtn.disabled = true;
      createBtn.style.opacity = "0.5";
    }
  }

  registerForm.addEventListener("input", checkRegisterReady);
  avatarRadios.forEach(r => r.addEventListener("change", checkRegisterReady));
}