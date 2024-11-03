// Check if dico_avenants_mois_ce is available
if (typeof dico_avenants_mois_ce !== 'undefined') {
    // Extract and sort dates chronologically in 'MM-YYYY' format
    var dates = Object.keys(dico_avenants_mois_ce).sort((a, b) => {
        const [monthA, yearA] = a.split('-').map(Number);
        const [monthB, yearB] = b.split('-').map(Number);
        return yearA - yearB || monthA - monthB;
    });

    // Map data to the sorted dates
    var avenantData = dates.map(date => dico_avenants_mois_ce[date] || 0);

    // Set up the Chart.js bar chart
    var ctx = document.getElementById('BarChartCE').getContext('2d');
    var BarChartCE = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,  // Dates as x-axis labels
            datasets: [
                {
                    label: 'Avenants',   // Single label for all bars
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    data: avenantData   // Data for avenant
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Allows chart to fill container's dimensions
            scales: {
                x: {
                    title: { display: true, text: 'Date' }
                },
                y: {
                    beginAtZero: true,
                    min: 0,
                    title: { display: true, text: 'Count' },
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return Number.isInteger(value) ? value : '';
                        }
                    }
                }
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: { enabled: true }
            }
        }
    });
} else {
    console.error('dico_avenants_mois_ce is not defined');
}
