/* ==========================================================================
   CivicPulse Dashboard Visualizations (Chart.js Integration)
   ========================================================================== */

function renderDashboardCharts(categoriesData, statusData, severityData, districtData) {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#64748B';

    // 1. Categories Chart (Doughnut)
    const catCanvas = document.getElementById('categoriesChart');
    if (catCanvas && categoriesData) {
        new Chart(catCanvas, {
            type: 'doughnut',
            data: {
                labels: Object.keys(categoriesData),
                datasets: [{
                    data: Object.values(categoriesData),
                    backgroundColor: [
                        '#0D9488', '#0284C7', '#EA580C', '#DC2626',
                        '#8B5CF6', '#059669', '#D97706', '#64748B'
                    ],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // 2. Status Chart (Doughnut)
    const statusCanvas = document.getElementById('statusChart');
    if (statusCanvas && statusData) {
        new Chart(statusCanvas, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusData),
                datasets: [{
                    data: Object.values(statusData),
                    backgroundColor: ['#F59E0B', '#3B82F6', '#8B5CF6', '#059669'],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // 3. Severity Level Chart (Bar)
    const severityCanvas = document.getElementById('severityChart');
    if (severityCanvas && severityData) {
        new Chart(severityCanvas, {
            type: 'bar',
            data: {
                labels: Object.keys(severityData),
                datasets: [{
                    label: 'Number of Reports',
                    data: Object.values(severityData),
                    backgroundColor: ['#2563EB', '#D97706', '#EA580C', '#DC2626'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    // 4. District Location Chart (Horizontal Bar)
    const districtCanvas = document.getElementById('districtChart');
    if (districtCanvas && districtData) {
        new Chart(districtCanvas, {
            type: 'bar',
            data: {
                labels: Object.keys(districtData),
                datasets: [{
                    label: 'Report Count',
                    data: Object.values(districtData),
                    backgroundColor: '#0F172A',
                    borderRadius: 8
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }
}
