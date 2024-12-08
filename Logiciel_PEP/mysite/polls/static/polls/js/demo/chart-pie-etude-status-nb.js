// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Extracting the keys (labels) and values (data) from the repartitionData object
var labels = Object.keys(repartitionData_nb);
var dataValues = Object.values(repartitionData_nb);

// Example colors (you can generate more if needed)
var dataColors = ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99'];

var ctx = document.getElementById("PieChartEtudeSatusnb");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: labels, // Using labels from the repartitionData object
    datasets: [{
      data: dataValues, // Using data values from the repartitionData object
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
    },
    legend: {
      display: false,  // Disable the default Chart.js legend
    },
    cutoutPercentage: 80,
  },
});
