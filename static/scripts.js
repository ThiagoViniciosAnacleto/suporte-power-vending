document.addEventListener("DOMContentLoaded", function () {
    const toast = document.getElementById("toast");
    if (toast) {
    setTimeout(function () {
        toast.style.display = "none";
    }, 4000);
}
});

document.addEventListener('DOMContentLoaded', function () {
    // Sempre aplica o darkmode salvo no localStorage, mesmo ao trocar de página
    if (localStorage.getItem('darkmode') === 'on') {
        document.body.classList.add('darkmode');
    } else {
        document.body.classList.remove('darkmode');
    }

    const btn = document.getElementById('toggle-darkmode');
    if (btn) {
        // Atualiza botão conforme modo
        function updateButton() {
            if (document.body.classList.contains('darkmode')) {
                btn.textContent = '☀️ Modo Claro';
            } else {
                btn.textContent = '🌙 Modo Escuro';
            }
        }
        updateButton();

        btn.onclick = function () {
            document.body.classList.toggle('darkmode');
            // Salva preferência
            if (document.body.classList.contains('darkmode')) {
                localStorage.setItem('darkmode', 'on');
            } else {
                localStorage.setItem('darkmode', 'off');
            }
            updateButton();
        };
    }
});
