// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Extracting the keys (labels) and values (data) from the repartitionData object
var labels = Object.keys(genre_inter);
var dataValues = Object.values(genre_inter);

// Example colors (you can generate more if needed)
var dataColors = [ '#FF33FF', '#FFFF99'];

var ctx = document.getElementById("PieChartGenreIntervenants");
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
