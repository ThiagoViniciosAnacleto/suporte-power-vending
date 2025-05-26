document.addEventListener("DOMContentLoaded", function () {
    // Toast
    const toast = document.getElementById("toast");
    if (toast) {
        setTimeout(function () {
            toast.style.display = "none";
        }, 4000);
    }

    // Darkmode
    if (localStorage.getItem('darkmode') === 'on') {
        document.body.classList.add('darkmode');
    } else {
        document.body.classList.remove('darkmode');
    }

    const btn = document.getElementById('toggle-darkmode');
    if (btn) {
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
            if (document.body.classList.contains('darkmode')) {
                localStorage.setItem('darkmode', 'on');
            } else {
                localStorage.setItem('darkmode', 'off');
            }
            updateButton();
        };
    }

    // Fechar modal ao clicar fora do conteúdo
    var modais = document.querySelectorAll('.modal-chamado');
    modais.forEach(function(modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});

// Funções globais para os modais
window.abrirModalChamado = function(id) {
    var modal = document.getElementById('modal-chamado-' + id);
    if (modal) {
        modal.style.display = 'flex';
    }
};

window.fecharModalChamado = function(id) {
    var modal = document.getElementById('modal-chamado-' + id);
    if (modal) {
        modal.style.display = 'none';
    }
};

function excluirChamado(id, csrf) {
    if (confirm('Tem certeza que deseja excluir este chamado?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/excluir/${id}`;

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = csrf;

        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}

function carregarConteudo(parcial) {
    fetch(parcial.startsWith('/conteudo/') ? parcial : `/conteudo/${parcial}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById("conteudo-dinamico").innerHTML = html;

            if (parcial === "dashboard") {
                inicializarDashboard(); // função do dashboard.js
            }
        });
}