document.addEventListener("DOMContentLoaded", () => {
    aplicarTemaDarkmode();
    configurarBotaoDarkmode();
    ativarInterceptacaoFormsSPA();
    observarToast();
    ocultarToast();
    configurarFechamentoModais();
});

// ✅ DARKMODE
function aplicarTemaDarkmode() {
    if (localStorage.getItem("darkmode") === "on") {
        document.body.classList.add("darkmode");
    }
}

function configurarBotaoDarkmode() {
    const btn = document.getElementById("toggle-darkmode");
    if (!btn) return;

    function updateTexto() {
        btn.textContent = document.body.classList.contains("darkmode")
            ? "☀️ Modo Claro"
            : "🌙 Modo Escuro";
    }

    updateTexto();

    btn.onclick = () => {
        document.body.classList.toggle("darkmode");
        localStorage.setItem("darkmode",
            document.body.classList.contains("darkmode") ? "on" : "off");
        updateTexto();
    };
}

// ✅ MODAIS
function configurarFechamentoModais() {
    document.querySelectorAll(".modal-chamado").forEach(modal => {
        modal.addEventListener("click", event => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    });
}

window.abrirModalChamado = id => {
    const modal = document.getElementById(`modal-chamado-${id}`);
    if (modal) modal.style.display = "flex";
};

window.fecharModalChamado = id => {
    const modal = document.getElementById(`modal-chamado-${id}`);
    if (modal) modal.style.display = "none";
};

// ✅ EXCLUSÃO DE CHAMADOS
function excluirChamado(id, csrf) {
    if (confirm("Tem certeza que deseja excluir este chamado?")) {
        const form = document.createElement("form");
        form.method = "POST";
        form.action = `/excluir/${id}`;

        const csrfInput = document.createElement("input");
        csrfInput.type = "hidden";
        csrfInput.name = "csrf_token";
        csrfInput.value = csrf;

        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}

// ✅ SPA: carregamento de partials + CSS dinâmico
function carregarConteudo(parcial) {
    const url = parcial.startsWith("/conteudo/") ? parcial : `/conteudo/${parcial}`;

    fetch(url)
        .then(res => res.text())
        .then(html => {
            const container = document.getElementById("conteudo-dinamico");
            container.innerHTML = html;

            ativarInterceptacaoFormsSPA();
            observarToast();
            carregarCssDinamico(url);

            // Detectar quando os gráficos forem injetados
            if (url.includes("dashboard")) {
                const dashObserver = new MutationObserver((mut, obs) => {
                    const s = document.getElementById("grafico-status");
                    const p = document.getElementById("grafico-prioridade");
                    const e = document.getElementById("grafico-empresa");
                    if (s && p && e) {
                        inicializarDashboard();
                        obs.disconnect();
                    }
                });
                dashObserver.observe(container, { childList: true, subtree: true });
            }
        })
        .catch(() => {
            document.getElementById("conteudo-dinamico").innerHTML = "<p>Erro ao carregar conteúdo.</p>";
        });
}

// ✅ CSS dinâmico por partial
function carregarCssDinamico(url) {
    const mapaCss = {
        "editar_chamado": "editar_chamado.css",
        // Você pode adicionar mais páginas aqui no futuro
    };

    Object.keys(mapaCss).forEach(chave => {
        if (url.includes(chave)) {
            const id = `css-${chave}`;
            if (!document.getElementById(id)) {
                const link = document.createElement("link");
                link.rel = "stylesheet";
                link.href = `/static/${mapaCss[chave]}`;
                link.id = id;
                document.head.appendChild(link);
            }
        }
    });
}

// ✅ SPA: interceptar formulários
function ativarInterceptacaoFormsSPA() {
    document.querySelectorAll("form[data-spa-post]").forEach(form => {
        if (form.dataset.listener) return;

        form.addEventListener("submit", async e => {
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
                ativarInterceptacaoFormsSPA();
            }
        });

        form.dataset.listener = "true";
    });
}

// ✅ Toast automático
function ocultarToast() {
    const tentarOcultar = () => {
        const toast = document.getElementById("toast");
        if (toast) {
            toast.style.opacity = "1";
            toast.style.transition = "opacity 0.5s ease";

            setTimeout(() => {
                toast.style.opacity = "0";
                setTimeout(() => {
                    toast.style.display = "none";
                }, 500);
            }, 3000);
        } else {
            setTimeout(tentarOcultar, 50);
        }
    };

    tentarOcultar();
}

// ✅ Monitorar quando um novo toast aparece
let toastObserver = null;

function observarToast() {
    const container = document.getElementById("conteudo-dinamico");
    if (toastObserver) toastObserver.disconnect();

    toastObserver = new MutationObserver(() => {
        const toast = document.getElementById("toast");
        if (toast) ocultarToast();
    });

    toastObserver.observe(container, { childList: true, subtree: true });
}
