var hamburger = document.getElementById("hamburger");
var overlay = document.getElementsByClassName("overlay")[0];

hamburger.addEventListener("click", function () {
  if (hamburger.classList.contains("open-hamburger")) {
    hamburger.classList.remove("open-hamburger");
    overlay.style.height = "0";
  } else {
    hamburger.classList.add("open-hamburger");
    overlay.style.height = "100vh";
  }
});

var project_pane = document.getElementsByClassName("project-pane")[0];
var ticket_pane = document.getElementsByClassName("ticket-pane")[0];
var project_info = document.getElementById("project-info");

var mobile_project_nav = document.getElementById("mobile-project-nav");
if (mobile_project_nav) {
  var mobile_nav_buttons = mobile_project_nav.children;
}

function openProjectPane() {
  project_pane.style.width = "100%";
  ticket_pane.style.width = "0";
  ticket_pane.style.paddingRight = "0";
  project_pane.style.paddingRight = "3rem";
  project_info.onclick = function() { closeProjectPane() };
  for (let i = 0; i < mobile_nav_buttons.length; i++) {
    mobile_nav_buttons[i].style.display = "block";
  }
  mobile_nav_buttons[0].firstChild.classList.remove("fa-bars")
  mobile_nav_buttons[0].firstChild.classList.add("fa-times")
}

function closeProjectPane() {
  project_pane.style.width = "0";
  ticket_pane.style.width = "100%";
  ticket_pane.style.paddingRight = "3rem";
  project_pane.style.paddingRight = "0";
  project_info.onclick = function() { openProjectPane() };
  for (let i = 1; i < mobile_nav_buttons.length; i++) {
    mobile_nav_buttons[i].style.display = "none";
  }
  mobile_nav_buttons[0].firstChild.classList.remove("fa-times")
  mobile_nav_buttons[0].firstChild.classList.add("fa-bars")
}

function filterTickets(checkbox) {
  var filterTarget = `${checkbox.value.toLowerCase()}-ticket`;
  var tickets = document.getElementsByClassName(filterTarget);

  if (checkbox.checked == false) {
    for (let i = 0; i < tickets.length; i++) {
      tickets[i].style.display = "none";
    };
  } else {
    for (let i = 0; i < tickets.length; i++) {
      tickets[i].style.display = "block";
    };
  };
};