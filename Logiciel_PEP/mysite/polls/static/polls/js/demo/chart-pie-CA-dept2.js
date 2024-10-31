// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


var labels2 = Object.keys(dico_ca_departement);
var dataValues2 = Object.values(dico_ca_departement);
var dataColors2 = ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99', '#00B3E6',  '#E6B333', '#3366E6']

// Example colors (you can generate more if needed)

var ctx2 = document.getElementById("PieChartCAdepartement");
var myPieChart2 = new Chart(ctx2, {
  type: 'doughnut',
  data: {
    labels: labels2, // Using labels from the repartitionData object
    datasets: [{
      data: dataValues2, // Using data values from the repartitionData object
      backgroundColor: dataColors2,
      hoverBackgroundColor: dataColors2.map(color => color.replace('#', '#ff')),
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
      display: true,  // Display the legend
      position: 'bottom',  // You can also use 'top', 'left', or 'right'
      labels: {
        boxWidth: 20,  // Size of the box next to the label
        padding: 15,  // Space between labels
      },
    },
    cutoutPercentage: 80,
  },
});
