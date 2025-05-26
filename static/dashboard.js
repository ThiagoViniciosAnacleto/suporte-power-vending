const socket = io(); // só conecta uma vez

function inicializarDashboard() {
    // Verifica se os elementos dos gráficos estão presentes
    const elStatus = document.getElementById('grafico-status');
    const elPrioridade = document.getElementById('grafico-prioridade');
    const elEmpresa = document.getElementById('grafico-empresa');

    if (!elStatus || !elPrioridade || !elEmpresa) return;

    const ctxStatus = elStatus.getContext('2d');
    const ctxPrioridade = elPrioridade.getContext('2d');
    const ctxEmpresa = elEmpresa.getContext('2d');

    const chartStatus = new Chart(ctxStatus, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{ label: 'Status', data: [], backgroundColor: '#4b91fa' }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });

    const chartPrioridade = new Chart(ctxPrioridade, {
        type: 'pie',
        data: {
            labels: [],
            datasets: [{ label: 'Prioridade', data: [], backgroundColor: ['#28a745', '#ffc107', '#dc3545'] }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const chartEmpresa = new Chart(ctxEmpresa, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{ label: 'Empresas', data: [], backgroundColor: ['#4b91fa', '#6f42c1', '#fd7e14', '#20c997', '#e83e8c'] }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // Evita duplicação do listener
    socket.off('dashboard_update');

    // Solicita dados atualizados
    socket.emit('solicitar_atualizacao');

    // Recebe dados do servidor e atualiza os gráficos
    socket.on('dashboard_update', (dados) => {
        console.log("[DEBUG] Dados recebidos do servidor:", dados);

        if (!dados || !dados.status || !dados.prioridade || !dados.empresas) {
            console.error("❌ Dados incompletos para renderizar gráficos");
            return;
        }

        chartStatus.data.labels = Object.keys(dados.status);
        chartStatus.data.datasets[0].data = Object.values(dados.status);
        chartStatus.update();

        chartPrioridade.data.labels = Object.keys(dados.prioridade);
        chartPrioridade.data.datasets[0].data = Object.values(dados.prioridade);
        chartPrioridade.update();

        chartEmpresa.data.labels = Object.keys(dados.empresas);
        chartEmpresa.data.datasets[0].data = Object.values(dados.empresas);
        chartEmpresa.update();
    });
}

function carregarDashboard() {
    fetch("/conteudo/dashboard")
        .then(res => res.text())
        .then(html => {
            document.querySelector("main").innerHTML = html;

            // Aguarda elementos <canvas> aparecerem no DOM
            const tentarIniciar = () => {
                const s = document.getElementById('grafico-status');
                const p = document.getElementById('grafico-prioridade');
                const e = document.getElementById('grafico-empresa');

                if (s && p && e) {
                    inicializarDashboard();
                } else {
                    setTimeout(tentarIniciar, 100); // tenta novamente
                }
            };

            tentarIniciar();
        });
}
