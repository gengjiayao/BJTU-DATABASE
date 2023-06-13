const dateInput = document.getElementById("date");
const today = new Date();
const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);
const fiveDaysLater = new Date(today.getTime() + 5 * 24 * 60 * 60 * 1000);
const tomorrowStr = tomorrow.toISOString().split('T')[0];
const fiveDaysLaterStr = fiveDaysLater.toISOString().split('T')[0];
dateInput.setAttribute("min", tomorrowStr);
dateInput.setAttribute("max", fiveDaysLaterStr);
