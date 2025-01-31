// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


var labels2 = Object.keys(CA_typeentreprise);
var dataValues2 = Object.values(CA_typeentreprise);
var dataColors2 = ['#0071C5', '#FFD700', '#DC143C', '#008B8B', '#B8860B', '#4682B4', '#DAA520', '#808080']; // Couleurs pour chaque secteur

// Example colors (you can generate more if needed)

var ctx2 = document.getElementById("PieChartCAtypeentreprise");
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


var labels = Object.keys(dico_ca_secteur);
var dataValues = Object.values(dico_ca_secteur);

// Example colors (you can generate more if needed)
var dataColors = ['#0071C5', '#FFD700', '#DC143C', '#008B8B', '#B8860B', '#4682B4', '#DAA520', '#808080']; // Couleurs pour chaque secteur

var ctx = document.getElementById("PieChartCAdSecteur");
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



