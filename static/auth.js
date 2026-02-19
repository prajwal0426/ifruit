const spotlight = document.getElementById("spotlight");
const loginBox = document.getElementById("loginBox");
const registerBox = document.getElementById("registerBox");

// spotlight ON only when page loads
window.onload = () => {
  spotlight.classList.add("on");
};

function openRegister() {
  loginBox.classList.add("hidden");
  registerBox.classList.remove("hidden");
}

function closeRegister() {
  registerBox.classList.add("hidden");
  loginBox.classList.remove("hidden");
}
