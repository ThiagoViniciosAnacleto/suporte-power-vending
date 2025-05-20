document.addEventListener("DOMContentLoaded", function () {
    const socket = io();

    // Gráficos base
    const ctxStatus = document.getElementById('grafico-status').getContext('2d');
    const ctxPrioridade = document.getElementById('grafico-prioridade').getContext('2d');
    const ctxEmpresa = document.getElementById('grafico-empresa').getContext('2d');

    const chartStatus = new Chart(ctxStatus, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Status', data: [], backgroundColor: '#4b91fa' }] },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });

    const chartPrioridade = new Chart(ctxPrioridade, {
        type: 'pie',
        data: { labels: [], datasets: [{ label: 'Prioridade', data: [], backgroundColor: ['#28a745', '#ffc107', '#dc3545'] }] },
        options: { responsive: true }
    });

    const chartEmpresa = new Chart(ctxEmpresa, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ label: 'Empresas', data: [], backgroundColor: ['#4b91fa', '#6f42c1', '#fd7e14', '#20c997', '#e83e8c'] }] },
        options: { responsive: true }
    });

    // Requisição inicial
    socket.emit('solicitar_atualizacao');

    // Escuta atualização do servidor
    socket.on('dashboard_update', (dados) => {
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
});
