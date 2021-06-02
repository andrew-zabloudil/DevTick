/* Opens/closes the mobile project pane on smaller screens. */
var project_pane = document.getElementsByClassName("project-pane")[0];
var ticket_pane = document.getElementsByClassName("ticket-pane")[0];
var project_info = document.getElementById("project-info");
var mobile_project_nav = document.getElementById("mobile-project-nav");
if (mobile_project_nav) {
  var mobile_nav_buttons = mobile_project_nav.children;
}

project_info.onclick = function() { openProjectPane() };

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

/* Allows the filter menu to be expanded/collapsed by the user. */
var filterDropdown = document.getElementsByClassName("filter-dropdown")[0];
if (filterDropdown) {
  filterDropdown.addEventListener("click", function() {
  var dropdownArrow = document.getElementsByClassName("dropdown-arrow")[0];
  var filterContainer = document.getElementsByClassName("filter-container")[0];

  if (filterDropdown.classList.contains("hidden")) {
    filterDropdown.classList.remove("hidden")
    dropdownArrow.classList.remove("fa-caret-down");
    dropdownArrow.classList.add("fa-caret-up");
    filterContainer.style.display = "flex";
  } else {
    filterDropdown.classList.add("hidden")
    dropdownArrow.classList.remove("fa-caret-up");
    dropdownArrow.classList.add("fa-caret-down");
    filterContainer.style.display = "none";
  }
});
}


/* Dynamically changes the tickets that are displayed by using checkboxes to filter them. */
var checkboxes = document.getElementsByClassName("checkbox");
for (let i = 0; i < checkboxes.length; i++) {
  checkboxes[i].onchange = function() {filterTickets(checkboxes[i])}
}

function filterTickets(checkbox) {
  if (checkbox.value.toLowerCase() != "open" && checkbox.value.toLowerCase() != "closed") {
    var toFilter = `${checkbox.value.toLowerCase().replace(' ', '-')}-ticket-container`;
    var filterTargets = document.getElementsByClassName(toFilter);

    if (checkbox.checked == false) {
      for (let i = 0; i < filterTargets.length; i++) {
        filterTargets[i].style.display = "none";
      };
    } else {
      for (let i = 0; i < filterTargets.length; i++) {
        filterTargets[i].style.display = "flex";
      };
    };
  } else {
    var toFilter = `${checkbox.value.toLowerCase().replace(' ', '-')}-ticket`;
    var filterTargets = document.getElementsByClassName(toFilter);

    if (checkbox.checked == false) {
      for (let i = 0; i < filterTargets.length; i++) {
        filterTargets[i].style.display = "none";
      };
    } else {
      for (let i = 0; i < filterTargets.length; i++) {
        filterTargets[i].style.display = "block";
      };
    };
  }
};

/* Handles delete confirmation window for project deletion. */
var deleteProject = document.getElementById("delete-button")
var deleteConfirmation = document.getElementById("delete-project")

deleteProject.onclick = function() {
  deleteConfirmation.style.display = "block";
}

var cancelDelete = document.getElementById("cancel-delete")
cancelDelete.onclick = function() {
  deleteConfirmation.style.display = "none";
}

var closeModal = document.getElementsByClassName("close-modal")[0]
closeModal.onclick = function() {
  deleteConfirmation.style.display = "none";
}

window.onclick = function(event) {
  if(event.target == deleteConfirmation) {
    deleteConfirmation.style.display = "none";
  }
}