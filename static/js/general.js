/* Allows mobile hamburger menu to open/close when clicked. */
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
