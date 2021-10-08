window.onload = () => {
    const search_bar = document.getElementById("defaultForm-search");
    search_bar.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            window.location.href = "/szukaj?query=" + search_bar.value
        }
    })
}

function redirect(href) {
    window.location.href = href;
}

function show_login() {
    
}