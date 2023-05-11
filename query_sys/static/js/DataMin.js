const dateInput = document.getElementById("date");
const today = new Date();
const BeijingTime = new Date(today.toLocaleString("zh-CN", {timeZone: "Asia/Shanghai"}));
const tomorrow = new Date(BeijingTime.getTime() + 24 * 2 * 60 * 60 * 1000);
const five = new Date(BeijingTime.getTime() + 24 * 6 * 60 * 60 * 1000);
const tomorrowStr = tomorrow.toISOString().substr(0, 10);
const fiveStr = five.toISOString().substr(0, 10);
dateInput.setAttribute("min", tomorrowStr);
dateInput.setAttribute("max", fiveStr)
