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

// Pie Chart Example
var ctx = document.getElementById("PieChartCASect");
var labels = ["Industrie", "Distribution", "Secteur Public", "Conseil", "Transport", "Numérique", "BTP", "Autre"]; // Labels des secteurs
var dataColors = ['rgb(0,154,166)', 'rgb(255,182,18)', 'rgb(130,190,0)', 'rgb(205,0,55)', 'rgb(161,0,107)', 'rgb(210,255,0)', 'rgb(0,136,206)', 'rgb(110,30,120)']; // Couleurs pour chaque secteur

var myPieChart3 = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: labels,
    datasets: [{
      data: chiffre_affaire_par_secteur, 
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
      display: false
    },
    cutoutPercentage: 80,
  },
});
