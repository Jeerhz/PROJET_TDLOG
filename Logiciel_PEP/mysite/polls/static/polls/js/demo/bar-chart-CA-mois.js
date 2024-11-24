
Chart.defaults.global.defaultFontFamily = 'Nunito, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

if (typeof dico_CA_mois !== 'undefined') {
    // Extract dates and values for 'envoyés' and 'signées'
    var dates = Object.keys(dico_avenants_mois_ce).sort((a, b) => {
        const [monthA, yearA] = a.split('-').map(Number);
        const [monthB, yearB] = b.split('-').map(Number);
        return yearA - yearB || monthA - monthB;  // Sort by year first, then by month
    });    
    var CAData = dates.map(date => dico_CA_mois[date]['CA'] || 0);
    

    

    // Set up the Chart.js bar chart
    var ctx = document.getElementById('BarChartCAmois').getContext('2d');
    var BarChartCAmois = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'CA',
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    data: CAData,
                    barThickness: 100,
                }
                
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, 
            scales: {
                x: {
                    title: { display: true, text: 'Date' },
                    categoryPercentage: 0.1,   // Controls width of the entire group (0 to 1)
                    barPercentage: 0.1   
                },
                y: {
                    beginAtZero: true,    // Ensure the y-axis starts at zero
                    min: 0,               // Force the minimum value to be 0
                    max: ymax,            // Set max to calculated ymax
                    ticks: {
                        stepSize: 1,       // Display increments of 1
                        callback: function(value) {
                            return Number.isInteger(value) ? value : '';  // Display only integers
                        }
                    },
                    title: { display: true, text: 'Count' }
                }
            },
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: { enabled: true }
            }
        }
    });
} else {
    console.error('dico_CA_mois is not defined');
}
