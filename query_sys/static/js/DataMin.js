const dateInput = document.getElementById("date");
const today = new Date();
const tomorrow = new Date(today.getTime() + 24 * 2 * 60 * 60 * 1000);
const tomorrowStr = tomorrow.toISOString().substr(0, 10);
dateInput.setAttribute("min", tomorrowStr);
