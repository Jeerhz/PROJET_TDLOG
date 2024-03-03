// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}


// Bar Chart Example
var ctx = document.getElementById("ChartPhases").getContext('2d');

    var myBarChart = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            // Utilisez les noms des phases comme étiquettes
            labels: ["Phase 1", "Phase 2", "Phase 3", "Phase 4"],
            datasets: [{
                // La donnée pourrait être la durée de chaque phase
                label: "Durée",
                backgroundColor: "#223754",
                hoverBackgroundColor: "#2e59d9",
                borderColor: "#223754",
                // La durée de chaque phase en jours/semaines/mois
                data: [10, 20, 30, 40], // Exemple de données, remplacez-les par les durées réelles
            }],
        },
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    // L'axe des x représente maintenant la durée
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        beginAtZero: true,
                        // Vous pouvez formater les ticks pour ajouter 'jours' ou 'semaines' après les valeurs
                        callback: function(value, index, values) {
                            return number_format(value) + ' jours'; // ou ' semaines'
                        }
                    },
                    maxBarThickness: 25,
                }],
                yAxes: [{
                    // L'axe des y montre les noms des phases
                    gridLines: {
                        color: "rgb(234, 236, 244)",
                        zeroLineColor: "rgb(234, 236, 244)",
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    }
                }],
            },
            legend: {
                display: false
            },
            tooltips: {
                // Les info-bulles peuvent afficher des informations supplémentaires
                callbacks: {
                    label: function(tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + number_format(tooltipItem.xLabel) + ' jours'; // ou ' semaines'
                    }
                }
            },
        }
    });