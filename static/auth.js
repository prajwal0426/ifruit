const spotlight = document.getElementById("spotlight");
const lightSwitch = document.getElementById("lightSwitch");

let lightOn = false;

/* TOGGLE LIGHT */
lightSwitch.onclick = () => {
  lightOn = !lightOn;
  lightSwitch.classList.toggle("on");
  spotlight.classList.toggle("on");
};

/* AUTO TURN OFF IF ERROR EXISTS */
const error = document.querySelector(".error");
if (error) {
  spotlight.classList.remove("on");
  lightSwitch.classList.remove("on");
  lightOn = false;
}
