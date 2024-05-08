<script>
  import { comment } from "svelte/internal";
   import Layout from "../Layout.svelte";
</script>

<head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script>

        // update these variables
        const link = "https://docs.google.com/spreadsheets/d/1IWH8ir6DXPLnBENRCogJhSuaSzRnr6qtOxgOq3n-tuM/edit#gid=0"
        const id = link.substring(link.indexOf("d/") + 2, link.indexOf("/edit"));

        // key setup through console.cloud.google.com
        // key should be safe to leave public since it is restricted to only the spreadsheet api
        const key = "AIzaSyAlVjsRdCfuHsRt5RXriI2dLDrAjwMiP0Y"
        const year1 = 2023        // change year based on firsty half of school year (ie 24/25 --> year1 = 2024)
        const title = "House Points Spring 2024"
        const colors = ['Orange', 'Green', 'Purple', 'Yellow', 'Blue']

        // Range D1 to Z1 is to get house names (assuming they may change)
        const housesURL = "https://sheets.googleapis.com/v4/spreadsheets/" + id + "/values/D1:Z1?key=" + key

        // Range A3:Hxx to collect as much data in spreadsheet as needed. Change "H" if more houses are added. Later logic will deal with cutting off unnecessary rows.
        const dataURL = "https://sheets.googleapis.com/v4/spreadsheets/" + id + "/values/A3:H99?key=" + key

        async function LoadGoogle(){

            if(typeof google != 'undefined' && google && google.load){

                google.charts.load('current', {'packages':['corechart']});

                let data;
                let points;
                let numData;
                let annotationData;
                let houses = [];
                let max = 0;

                fetch(housesURL)
                    .then(res => {
                        return res.json();
                    })
                    .then(output => {
                        houses = output["values"][0];
                        tryDrawChart();
                    })
                    .catch(error => console.log(error));
            
                
                fetch(dataURL)
                    .then(res => {
                        return res.json();
                    })
                    .then(output => {
                        data = output["values"];
                        tryDrawChart();
                    })
                    .catch(error => console.log(error));

                function updateData() {

                    let currRow = 0;
                    dateData = [];
                    numData = [];
                    hoverData = [];
                    prevTemp = [0,0,0,0,0]

                    while(data[currRow][0] != '') {
                        const dateString = data[currRow][0]
                        const month = parseInt(dateString.substring(0, dateString.indexOf('/'))) - 1
                        const day = parseInt(dateString.substring(dateString.indexOf('/') + 1))

                        // basically check if we're in the in late year1 or early year2
                        const year = year1 + (month < 7)
                        let date = new Date(year, month, day)

                        let numTemp = data[currRow].slice(3)
                        let hoverTemp = []

                        for (let i = 0; i < numTemp.length; i++) {
                            numTemp[i] = parseFloat(numTemp[i]) + prevTemp[i];
                            hoverTemp.push(numTemp[i] + "\n" + data[currRow][i + 3] + " points earned\n" + data[currRow][1] + "\n" + date.toLocaleDateString('en-US'))
                        }
                        dateData.push(date)
                        numData.push(numTemp)
                        hoverData.push(hoverTemp)
                        currRow++;
                        prevTemp = numTemp;
                    }

                    let rowMax = numData.map(function(row){ return Math.max(...row) })
                    max = Math.max(...rowMax) * 1.3
                }

                window.addEventListener("resize", () => {
                    tryDrawChart();
                });

                function tryDrawChart() {
                    console.log("try");

                    if (!data || houses.length === 0) {
                        return;
                    }

                    console.log("success")

                    updateData();

                    var dataTable = new google.visualization.DataTable();
                    dataTable.addColumn('date', 'Day');
                    for (let i = 0; i < houses.length; i++) {
                        dataTable.addColumn('number', houses[i]); 
                        dataTable.addColumn({type:'string', role:'tooltip'});
                    }
                    
                    for (let i = 0; i < numData.length; i++) {
                        let newRow = [dateData[i]]
                        for (let j = 0; j < houses.length; j++) {
                            newRow.push(numData[i][j])
                            newRow.push(hoverData[i][j]);
                        }
                        dataTable.addRow(newRow)
                    }

                    var options = {
                        legend: 'right',
                        title: title,
                        width: '100%',
                        height: '100%',
                        colors: colors, 
                        vAxis: {
                            title: "House Points",
                            viewWindow: {
                                min: 0,
                                max: max
                            }
                        },
                        hAxis: {
                            title: "Houses"
                        }
                    };

                    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
                    chart.draw(dataTable, options);
                }
            } else {
                setTimeout(LoadGoogle, 30);
            }
        }
    
        LoadGoogle();
    </script>
</head>

<Layout>
    <div style="padding-left:50px">
        <h1 style="margin-left: 15px">Houses</h1>
    </div>
    {#if window.innerWidth > 769}
        <div style="height: 80vh">
            <div id="chart_div"/>
        </div>
    {:else}
        <div style="height: 70vh">
            <div id="chart_div"/>
        </div>
    {/if}
</Layout>

<style>
    #chart_div {
        width: 100%;
        height: 100%;
    }
</style>