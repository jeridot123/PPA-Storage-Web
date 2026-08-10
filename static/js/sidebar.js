document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("toggleSidebar");

    console.log(sidebar)
    console.log(toggle)

    toggle.addEventListener("click", () => {
        console.log('Button clicked"');
        sidebar.classList.toggle("collapsed");
    });

});