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
var ctx = document.getElementById("PieChartCAType");
var labels = ["Grande Entreprise", "Secteur Public", "Start-Up et TPE", "PME", "ETI", "Association"];
var dataColors = ['#4A90E2', '#D0021B', '#7B8D8E', '#F5A623', '#8B572A', '#50E3C2'];
var myPieChart2 = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: labels,
    datasets: [{
      data: chiffre_affaire_par_type, 
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
