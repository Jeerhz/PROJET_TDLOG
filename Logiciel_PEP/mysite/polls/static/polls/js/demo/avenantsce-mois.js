// Check if dico_suivi_devis is available
if (typeof dico_avenants_mois_ce !== 'undefined') {
    // Extract dates and values for 'envoyés' and 'signées'
    var dates = Object.keys(dico_avenants_mois_ce).sort((a, b) => {
        const [monthA, yearA] = a.split('-').map(Number);
        const [monthB, yearB] = b.split('-').map(Number);
        return yearA - yearB || monthA - monthB;  // Sort by year first, then by month
    });    
    var avenantsData = dates.map(date => dico_avenants_mois_ce[date]['avenants'] || 0);
    var avdelData = dates.map(date => dico_avenants_mois_ce[date]['délais'] || 0);
    var avbudgData = dates.map(date => dico_avenants_mois_ce[date]['budget'] || 0);

    // Determine the maximum y-axis value (ymax)
    var allValues = envoyesData.concat(signeesData);
    var ymax = Math.ceil(Math.max(...allValues) + 1);  // Add buffer to ymax

    // Set up the Chart.js bar chart
    var ctx = document.getElementById('BarChartCE').getContext('2d');
    var BarChartCE = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Avenants',
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    data: avenantsData,
                    barThickness: 60,
                },
                {
                    label: 'Délais',
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    data: avdelData,
                    barThickness: 60,
                },
                {
                    label: 'Budget',
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',  // Soft pink-red
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    data: avbudgData,
                    barThickness: 60,
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
    console.error('dico_avenants_mois_ce is not defined');
}
