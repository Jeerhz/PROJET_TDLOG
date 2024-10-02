// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Fonction pour générer des couleurs
function generateColors(count) {
  const colors = [];
  for (let i = 0; i < count; i++) {
    // Générer une couleur en hexadécimal
    const color = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
    colors.push(color);
  }
  return colors;
}

// your_chart_script.js
document.addEventListener('DOMContentLoaded', function () {
    // Use the etudeData variable defined in your Django template
    if (typeof etudeData !== 'undefined') {
        var dataPiechart = [
            parseFloat(etudeData.marge_JE.replace(',', '.')),
            parseFloat(etudeData.charges_URSSAF.replace(',', '.')),
            parseFloat(etudeData.retributions_totales.replace(',', '.'))
        ];

        var ctx = document.getElementById("PieChartEtude");
        var dataColors = ['#24569a', '#36b9cc', '#1cc88a'];

        var myPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['', '', ''],
                datasets: [{
                    data: dataPiechart,
                    backgroundColor: dataColors,
                    hoverBackgroundColor: dataColors.map(color => color.replace('#', '#ff')),
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                }],
            },
            options: {
                maintainAspectRatio: false,
                tooltips: {
                    backgroundColor: "rgb(255,255,255)",
                    bodyFontColor: "#858796",
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    caretPadding: 10,
                    callbacks: {
                        label: function (tooltipItem, data) {
                            var dataset = data.datasets[tooltipItem.datasetIndex];
                            var currentValue = dataset.data[tooltipItem.index];
                            return currentValue.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' }).replace(/\./g, ',');
                        }
                    }
                },
                legend: {
                    display: false,
                },
                cutoutPercentage: 80,
            },
        });
    } else {
        console.log('No etudeData available for this page.');
    }

});
