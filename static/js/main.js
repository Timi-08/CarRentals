// FAST CARS - shared JavaScript (loaded on every page from base.html)

document.addEventListener("DOMContentLoaded", function () {
  // 1. Highlight the navbar link for the page we are on.
  var path = window.location.pathname;
  document.querySelectorAll(".fc-navbar .navbar-nav .nav-link[href]").forEach(function (link) {
    var href = link.getAttribute("href");
    if (!href || href === "#") return;
    var isHome = href === "/" && path === "/";
    var isSection = href !== "/" && path.indexOf(href) === 0;
    if (isHome || isSection) link.classList.add("active");
  });

  // 2. Auto-dismiss success and info messages after 5 seconds.
  //    Errors and warnings stay until the user closes them.
  document.querySelectorAll("#message-area .alert-success, #message-area .alert-info").forEach(function (alertEl) {
    setTimeout(function () {
      if (window.bootstrap && bootstrap.Alert) {
        bootstrap.Alert.getOrCreateInstance(alertEl).close();
      } else {
        alertEl.remove();
      }
    }, 5000);
  });

  // 3. Mark invalid form fields (Django adds .errorlist next to bad fields).
  document.querySelectorAll(".field-group").forEach(function (group) {
    if (group.querySelector(".field-error")) {
      var input = group.querySelector("input, select, textarea");
      if (input) input.classList.add("is-invalid");
    }
  });
});
