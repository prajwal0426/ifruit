const spotlight = document.getElementById("spotlight");
const switchBtn = document.getElementById("lightSwitch");
const authBox = document.getElementById("authBox");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const title = document.getElementById("formTitle");

let isOn = false;

switchBtn.onclick = () => {
  isOn = !isOn;
  switchBtn.classList.toggle("on");
  spotlight.classList.toggle("on");
  authBox.classList.toggle("show");
};

/* REGISTER TOGGLE */
function showRegister() {
  loginForm.style.display = "none";
  registerForm.style.display = "block";
  title.innerText = "Register";
}

function showLogin() {
  registerForm.style.display = "none";
  loginForm.style.display = "block";
  title.innerText = "Login";
}

/* AUTO OFF ON ERROR */
const error = document.querySelector(".error");
if (error) {
  spotlight.classList.remove("on");
  switchBtn.classList.remove("on");
  authBox.classList.remove("show");
  isOn = false;
}
