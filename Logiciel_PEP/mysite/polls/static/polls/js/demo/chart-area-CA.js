Chart.defaults.global.defaultFontFamily = 'Nunito, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        s = '',
        toFixedFix = function(n, prec) {
            var k = Math.pow(10, prec);
            return '' + (Math.round(n * k) / k).toFixed(prec);
        };
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

var ctx = document.getElementById("myAreaChart1");
var myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: "Earnings",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "rgba(78, 115, 223, 1)",
            pointRadius: 3,
            pointBackgroundColor: "rgba(78, 115, 223, 1)",
            pointBorderColor: "rgba(78, 115, 223, 1)",
            pointHoverRadius: 3,
            pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
            pointHoverBorderColor: "rgba(78, 115, 223, 1)",
            pointHitRadius: 10,
            pointBorderWidth: 2,
            data: [],
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
                type: 'time',
                time: {
                    parser: 'YYYY-MM',
                    unit: 'month',
                    tooltipFormat: 'YYYY-MM',
                    displayFormats: {
                        month: 'YYYY-MM'
                    }
                },
                gridLines: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    maxTicksLimit: 10,
                    autoSkip: true,
                    maxRotation: 0,
                    callback: function(value, index, values) {
                        return value;
                    }
                }
            }],
            yAxes: [{
                ticks: {
                    maxTicksLimit: 5,
                    padding: 10,
                    callback: function(value, index, values) {
                        return '$' + number_format(value);
                    }
                },
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
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: 'index',
            caretPadding: 10,
            callbacks: {
                label: function(tooltipItem, chart) {
                    var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                    return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
                }
            }
        }
    }
});

function fetchAndUpdateChart() {
    var startDate = document.getElementById('start_date').value;
    var endDate = document.getElementById('end_date').value;

    console.log('Fetching data for:', startDate, 'to', endDate);  // Debug print

    fetch(`/polls/fetch_data?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            console.log('Fetched data:', data);  // Debug print

            if (data.error) {
                console.error('Error fetching data:', data.error);
                return;
            }

            myLineChart.data.labels = data.date_labels;
            myLineChart.data.datasets[0].data = data.cumulated_CA;
            myLineChart.update();
            
            // Update debug information
            document.getElementById('chartLabels').textContent = JSON.stringify(data.date_labels, null, 2);
            document.getElementById('chartDataPoints').textContent = JSON.stringify(data.cumulated_CA, null, 2);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function updateChart() {
    fetchAndUpdateChart();
}

function downloadChart() {
    var link = document.createElement('a');
    link.href = myLineChart.toBase64Image();
    link.download = 'chart.png';
    link.click();
}

// Fetch and update chart on page load
document.addEventListener('DOMContentLoaded', function() {
    fetchAndUpdateChart();
});



// Ensure updateChart is globally accessible
window.updateChart = updateChart;
