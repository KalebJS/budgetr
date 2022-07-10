$(document).ready(function () {
    let el = document.getElementById("pieChart");
    if (el != null && pieChartLabels != null && pieChartData != null) {

        let colorSchema = {
            red: {
                background: "#F7464A",
                hoverBackground: "#FF5A5E"
            },
            green: {
                background: "#46CFBD",
                hoverBackground: "#5AE3D1"
            }
        }
        let backgroundColors = []
        let hoverBackgroundColors = []
        for (let i = 0; i < colorsCoding.length; i++) {
            backgroundColors.push(colorSchema[colorsCoding.at(i)]["background"]);
            hoverBackgroundColors.push(colorSchema[colorsCoding[i]]["hoverBackground"]);
        }

        let ctxP = el.getContext('2d');
        let myPieChart = new Chart(ctxP, {
            type: 'pie',
            data: {
                labels: pieChartLabels,
                datasets: [{
                    data: pieChartData,
                    backgroundColor: backgroundColors,
                    hoverBackgroundColor: hoverBackgroundColors
                }]
            },
            options: {
                responsive: true,
                legend: {
                    display: false,
                },
                elements: {
                    arc: {
                        borderWidth: 0
                    }
                }
            }
        });
    }
});