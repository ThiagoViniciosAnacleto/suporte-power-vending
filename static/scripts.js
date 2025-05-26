document.addEventListener("DOMContentLoaded", function () {
    ativarInterceptacaoFormsSPA();
    ocultarToast();

    // ✅ Darkmode toggle
    if (localStorage.getItem('darkmode') === 'on') {
        document.body.classList.add('darkmode');
    }

    const btn = document.getElementById('toggle-darkmode');
    if (btn) {
        function updateButton() {
            btn.textContent = document.body.classList.contains('darkmode')
                ? '☀️ Modo Claro'
                : '🌙 Modo Escuro';
        }

        updateButton();

        btn.onclick = () => {
            document.body.classList.toggle('darkmode');
            localStorage.setItem('darkmode',
                document.body.classList.contains('darkmode') ? 'on' : 'off');
            updateButton();
        };
    }

    // ✅ Fechar modal ao clicar fora
    document.querySelectorAll('.modal-chamado').forEach(modal => {
        modal.addEventListener('click', event => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});

// ✅ Funções globais
window.abrirModalChamado = function (id) {
    const modal = document.getElementById('modal-chamado-' + id);
    if (modal) modal.style.display = 'flex';
};

window.fecharModalChamado = function (id) {
    const modal = document.getElementById('modal-chamado-' + id);
    if (modal) modal.style.display = 'none';
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

// ✅ Carregamento SPA de conteúdo parcial
function carregarConteudo(parcial) {
    const url = parcial.startsWith("/conteudo/") ? parcial : `/conteudo/${parcial}`;

    fetch(url)
        .then(res => res.text())
        .then(html => {
            const container = document.getElementById("conteudo-dinamico");
            container.innerHTML = html;

            ativarInterceptacaoFormsSPA();
            ocultarToast();

            if (url.includes("dashboard")) {
                const observer = new MutationObserver((mut, obs) => {
                    const s = document.getElementById('grafico-status');
                    const p = document.getElementById('grafico-prioridade');
                    const e = document.getElementById('grafico-empresa');
                    if (s && p && e) {
                        inicializarDashboard();
                        obs.disconnect();
                    }
                });

                observer.observe(container, { childList: true, subtree: true });
            }
        })
        .catch(() => {
            document.getElementById("conteudo-dinamico").innerHTML = "<p>Erro ao carregar conteúdo.</p>";
        });
}

function ativarInterceptacaoFormsSPA() {
    document.querySelectorAll("form[data-spa-post]").forEach(form => {
        if (!form.dataset.listener) {
            form.addEventListener("submit", async function (e) {
                e.preventDefault();
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData
                });

                if (response.redirected) {
                    carregarConteudo(response.url);
                } else {
                    const html = await response.text();
                    document.getElementById("conteudo-dinamico").innerHTML = html;
                    ativarInterceptacaoFormsSPA(); // 👈 reaplica após renderizar novo conteúdo
                }
            });
            form.dataset.listener = "true"; // evita adicionar mais de uma vez
        }
    });
}

function ocultarToast() {
    requestAnimationFrame(() => {
        const toast = document.getElementById("toast");
        if (toast) {
            // Garante estilos iniciais
            toast.style.opacity = "1";
            toast.style.transition = "opacity 0.5s ease";

            // Aguarda renderização visual
            setTimeout(() => {
                toast.style.opacity = "0";

                // Remove após fade-out
                setTimeout(() => {
                    toast.style.display = "none";
                }, 500);
            }, 3000); // visível por 3s
        }
    });
}

