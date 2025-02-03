const navBar = document.querySelector("nav"),
    menuBtns = document.querySelectorAll(".menu-icon"),
    overlay = document.querySelector(".overlay"),
    topLogo = document.querySelector("#topLogo");
menuBtns.forEach((menuBtn) => {
    menuBtn.addEventListener("click", () => {
        navBar.classList.toggle("open");
        topLogo.classList.toggle("hide");
    });
});
overlay.addEventListener("click", () => {
    navBar.classList.remove("open");
    topLogo.classList.remove("hide");
});
$(function () {
    $('[data-toggle="tooltip"]').tooltip({
        trigger: 'hover',
        container: 'body'
    });
    menuBtns.forEach((menuBtn) => {
        menuBtn.addEventListener("click", () => {
            $('[data-toggle="tooltip"]').tooltip('hide');
        });
    });
});
function handleTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const icon = themeToggle.querySelector('i');
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    icon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        const tooltipText = newTheme === 'dark' ? 'Modo claro' : 'Modo oscuro';
        $(themeToggle).attr('title', tooltipText).tooltip('dispose').tooltip();
    });
}
document.addEventListener('DOMContentLoaded', () => {
    handleTheme();
});