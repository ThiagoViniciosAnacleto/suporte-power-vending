document.addEventListener("DOMContentLoaded", function () {
    const toast = document.getElementById("toast");
    if (toast) {
    setTimeout(function () {
        toast.style.display = "none";
    }, 4000);
}
});