<script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
<script src="js/outerLabels.js"></script>

<script type="text/javascript">
   var selectors = document.getElementById('selectors').innerHTML;

   if (selectors == 1) {
      show('chartselect1img');
      document.getElementById('chartselect1round').style.background = '#99cc66';
   }
   if (selectors == 2) {
      show('chartselect2img');
      document.getElementById('chartselect2round').style.background = '#ffd966';
   }
   if (selectors == 3) {
      show('chartselect3img');
      document.getElementById('chartselect3round').style.background = '#ff9999';
   }


//   alert(selectors);
   var chart_1_data_1 = document.getElementById('chart_1_data_1').innerHTML;
   var chart_1_data_2 = document.getElementById('chart_1_data_2').innerHTML;
   var chart_1_data_3 = document.getElementById('chart_1_data_3').innerHTML;

   var chart_2_data_1 = document.getElementById('chart_2_data_1').innerHTML;
   var chart_2_data_2 = document.getElementById('chart_2_data_2').innerHTML;


   var heighty = parseInt(chart_2_data_1) + parseInt(chart_2_data_2);
   heighty = 0 - 55 - (heighty*2);
   if (heighty < -190) {
       heighty = -185;
   }
   document.getElementById('bar-inner').style.marginTop = heighty+'px';




// var ctx = document.getElementById('myChart').getContext('2d');
   var ctx = $('#myChart');
   var chart = new Chart(ctx, {
   plugins: [{
      beforeInit: (chartInstance, options) => {
         chartInstance.outerLabels = new OuterLabels();
         chartInstance.outerLabels.init(chartInstance);
         chartInstance.outerLabels.configure(options);
      },
      afterDatasetsDraw: chartInstance => {
         const dataset = chartInstance.config.data.datasets[0];
         chartInstance.outerLabels.resolveDataset(dataset);
         chartInstance.outerLabels.drawLabels(dataset);
      }

   }],
    // The type of chart we want to create
    type: 'doughnut',

    // The data for our dataset
    data: {
        labels: ['%', '%', '%'],
        datasets: [{
            backgroundColor: [ '#9400d3', '#ff99ff', '#ccc' ],
            borderColor: 'rgb(255, 255, 255)',
            data: [chart_1_data_1, chart_1_data_2, chart_1_data_3],

        }],
    },
    // Configuration options go here
    options: {
       legend: {
          display: false
       },
       layout: {
            padding: {
                left: 10,
                right: 10,
                top: 10,
                bottom: 10
            }
        },
       responsive: true,
       maintainAspectRatio: false,
       tooltips: {
          mode: false,
          callbacks: {
             title: function() {},
             label: function() {}
          }
       },
       cutoutPercentage: 60
    }
});

//   var ctx2 = $('#myChart2');
   var ctx2 = document.getElementById("myChart2").getContext("2d");
   var chart2 = new Chart(ctx2, {
      type: 'bar',
      data: {
         title: {
            display: true
         },
         datasets: [
         {
           label: '%',
           data: [chart_2_data_1],
           backgroundColor: '#9400d3' // green
         },
         {
           label: '%',
           data: [chart_2_data_2],
           backgroundColor: '#ff99ff' // yellow
         }]

      },
      options: {
         labels: { fontStyle: 'bold' },
         scales: {
            xAxes: [{
               stacked: true,
               ticks: {
                  beginAtZero: true
               }
            }],
            yAxes: [{
               stacked: true,
               gridLines: {
                  drawBorder: false
               },
               ticks: {
                  suggestedMin: 0,
                  suggestedMax: 100,
                  beginAtZero: true,
                  fontSize: 1,
                  display: false,
                  callback: function(value, index, values) {
//                    return value + '%';
                    return '';
                  }
               }
            }]
         },
         legend: {
          display: false
         },
         responsive: true,
         maintainAspectRatio: false,
         layout: {
            padding: {
                left: 40,
                right: 0,
                top: 10,
                bottom: 0
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        tooltips: {
          callbacks: {
             title: function() {},
             label: function(tooltipItem) {
               return tooltipItem.yLabel + '%';
             }
          }
       },

      }
   });

// в функцию можно добавить изменение значения в центре круглого графика, если необходимо
   function show(id){
      document.getElementById(id).style.display = 'block';
   };
   function hide(id){
      document.getElementById(id).style.display = 'none';
   };

//   $('#chartselect1').mouseover(function() { show('chartselect1img'); });
//   $('#chartselect1').mouseout(function() { hide('chartselect1img'); });
//
//   $('#chartselect2').mouseover(function() { show('chartselect2img'); });
//   $('#chartselect2').mouseout(function() { hide('chartselect2img'); });
//
//   $('#chartselect3').mouseover(function() { show('chartselect3img'); });
//   $('#chartselect3').mouseout(function() { hide('chartselect3img'); });


//   $('bar-inner').
</script>
