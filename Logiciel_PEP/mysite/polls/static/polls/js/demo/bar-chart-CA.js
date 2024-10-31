// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.family = 'Nunito, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.color = '#858796';

// Extract labels and data from the bar_chart_CA object
const labels = [];
const dataValues = [];

// Loop through the dictionary to extract months and earnings
for (const [year, months] of Object.entries(bar_chart_CA)) {
    for (const [month, earnings] of Object.entries(months)) {
        labels.push(`${year}-${String(month).padStart(2, '0')}`);  // Format as YYYY-MM
        dataValues.push(earnings);
    }
}

// Create the bar chart
const ctx = document.getElementById("monthlyEarningsChart1").getContext("2d");
const monthlyEarningsChart1 = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,  // Months in YYYY-MM format
        datasets: [{
            label: 'Monthly Earnings (€)',
            data: dataValues,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Earnings (€)'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Month'
                }
            }
        },
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            },
            tooltip: {
                enabled: true
            }
        }
    }
});
