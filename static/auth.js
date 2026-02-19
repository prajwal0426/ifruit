const spotlight = document.getElementById("spotlight");
const switchBtn = document.getElementById("lightSwitch");
const loginBox = document.getElementById("loginBox");

let isOn = false;

switchBtn.onclick = () => {
  isOn = !isOn;

  switchBtn.classList.toggle("on");
  spotlight.classList.toggle("on");
  loginBox.classList.toggle("show");
};

/* AUTO TURN OFF IF ERROR */
const error = document.querySelector(".error");
if (error) {
  spotlight.classList.remove("on");
  switchBtn.classList.remove("on");
  loginBox.classList.remove("show");
  isOn = false;
}
