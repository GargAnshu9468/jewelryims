document.addEventListener("DOMContentLoaded", function () {
    const themeToggler = document.getElementById("theme-toggler");
    const body = document.body;

    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        themeToggler.innerHTML = '<i class="fas fa-sun"></i>';
    }

    themeToggler.addEventListener("click", function () {
        body.classList.toggle("dark-mode");

        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
            themeToggler.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            localStorage.setItem("theme", "light");
            themeToggler.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
});
