<script>
    import Layout from "../Layout.svelte";
</script>

<head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script>

        // update these variables
        const link = "https://docs.google.com/spreadsheets/d/1g2DfuqFoxLIOpmO5R3oNb3JSrA3Jwuvvk4CJZEVFtdU/edit?gid=0#gid=0"
        const id = link.substring(link.indexOf("d/") + 2, link.indexOf("/edit"));

        // key setup through console.cloud.google.com
        // key should be safe to leave public since it is restricted to only the spreadsheet api
        const key = "AIzaSyAlVjsRdCfuHsRt5RXriI2dLDrAjwMiP0Y"
        const year1 = 2024        // change year based on firsty half of school year (ie 24/25 --> year1 = 2024)
        const title = "Spring 2024 Points"
        const colors = ['Orange', 'Green', 'Purple', 'Red', 'Blue']

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

                // get list of house names from spreadsheet (in case they change)
                fetch(housesURL)
                    .then(res => {
                        return res.json();
                    })
                    .then(output => {
                        houses = output["values"][0];
                        tryDrawChart();
                        getIndividualData();
                    })
                    .catch(error => console.log(error));
            
                // get points data from spreadsheet
                fetch(dataURL)
                    .then(res => {
                        return res.json();
                    })
                    .then(output => {
                        data = output["values"];
                        tryDrawChart();
                    })
                    .catch(error => console.log(error));
                
                let name = ""

                function getIndividualData() {

                    fetch(`/api/profile/self/`)
                        .then(res => {
                            return res.json();
                        })
                        .then(userData => {
                            name = userData.first_name + userData.last_name;
                            return name
                        })
                        .then(name => {

                            for (let i = 0; i < houses.length; i++) {
                                fetch("https://sheets.googleapis.com/v4/spreadsheets/" + id + "/values/'" + houses[i] + "'!C1:Z2?key=" + key)
                                    .then(res => {
                                        return res.json();
                                    })
                                    .then(output => {
                                        let data = output["values"]
                                        for (let j = 0; j < data[0].length; j++) {
                                            console.log(data[0][j]);
                                            if (name === data[0][j]) {
                                                // document.getElementById("houseId").innerHTML = "Your House: " + houses[i];
                                                // document.getElementById("pointsId").innerHTML = "Your Points: " + data[1][j];
                                                found = true;
                                            }
                                        }
                                    })
                            }
                            
                        })
                }


                function updateData() {

                    let currRow = 0;
                    numData = [];
                    hoverData = [];

                    // Keeps track of accumulating scores over time (each spreadsheet row only shows points earned at that event)
                    prevTemp = [0,0,0,0,0]

                    while(data[currRow][0] != '') {
                        // get dates
                        const dateString = data[currRow][0]
                        const month = parseInt(dateString.substring(0, dateString.indexOf('/'))) - 1
                        const day = parseInt(dateString.substring(dateString.indexOf('/') + 1))

                        // basically check if we're in the in late year1 or early year2
                        const year = year1 + (month < 7)
                        let date = new Date(year, month, day)

                        let numTemp = data[currRow].slice(3)
                        let hoverTemp = []

                        // for each row of data, add point values on top of existing point values
                        for (let i = 0; i < numTemp.length; i++) {
                            numTemp[i] = parseFloat(numTemp[i]) + prevTemp[i];
                            hoverTemp.push("House " + houses[i] + "\n" + "\n" + numTemp[i] + " Points\n" + data[currRow][i + 3] + " points earned\n" + data[currRow][1] + "\n" + date.toLocaleDateString("en-US"))
                        }

                        // numData is all the points data
                        numData.push(numTemp)

                        // hoverData is the tooltips that appear when hovering over a point on the line graph
                        hoverData.push(hoverTemp)
                        currRow++;
                        prevTemp = numTemp;
                    }

                    let rowMax = numData.map(function(row){ return Math.max(...row) })
                    max = Math.max(...rowMax) * 1.3
                }

                // on resize, redraw the chart to fit hopefully
                window.addEventListener("resize", () => {
                    tryDrawChart();
                });

                function tryDrawChart() {

                    // first make sure that data has been retrieved
                    if (!data || houses.length === 0) {
                        return;
                    }

                    updateData();

                    // Building Line Chart

                    var lineDataTable = new google.visualization.DataTable();
                    lineDataTable.addColumn('number', 'Event Number');
                    for (let i = 0; i < houses.length; i++) {
                        lineDataTable.addColumn('number', houses[i]); 
                        lineDataTable.addColumn({type:'string', role:'tooltip'});
                    }

                    // Initialize Starting Point (all houses start at 0 points)
                    let startRow = [0]
                    for (let i = 0; i < houses.length; i++) {
                        startRow.push(0)
                        startRow.push("House " + houses[i] + "\nStarting Point\n0 Points")
                    }
                    lineDataTable.addRow(startRow)
                    
                    // add each row of data (each row represents 1 event)
                    for (let i = 0; i < numData.length; i++) {
                        let newRow = [i + 1]
                        for (let j = 0; j < houses.length; j++) {
                            newRow.push(numData[i][j])
                            newRow.push(hoverData[i][j]);
                        }
                        lineDataTable.addRow(newRow)
                    }

                    var lineOptions = {
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
                            title: "Event Count",
                            gridlines: { count: 20}
                        }
                    };

                    // Building Bar Chart

                    // get last entry in numData (current scores)
                    var currentScores = numData[numData.length - 1]
                    
                    barData = [['House', 'Points', { role: 'style'}]]

                    // add each house, score, color triplet one by one
                    for (var i = 0; i < houses.length; i++) {
                        barData.push([houses[i], currentScores[i], colors[i]])
                    }

                    // convert to google Data Table
                    var barDataTable = google.visualization.arrayToDataTable(barData)

                    var barOptions = {
                        title: title,
                        width: '100%',
                        height: '100%',
                        legend: { position: "none" },
                        vAxis: {
                            title: "House Points",
                            viewWindow: {
                                min: 0,
                                max: max
                            }
                        },
                        hAxis: {
                            title: "Houses",
                        }
                    }

                    // Draw default chart (line chart)
                    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
                    chart.draw(lineDataTable, lineOptions);

                    // Add button listener to switch to line chart
                    document.getElementById("line_button").addEventListener("click", () => {
                        var lineChart = new google.visualization.LineChart(document.getElementById('chart_div'));
                        lineChart.draw(lineDataTable, lineOptions);
                    })

                    // Add button listener to switch to bar chart
                    document.getElementById("bar_button").addEventListener("click", () => {
                        var barChart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
                        barChart.draw(barDataTable, barOptions)
                    })
                }
            } else {
                // if google hasn't loaded in yet, retry in a sec
                setTimeout(LoadGoogle, 30);
            }
        }
        
        LoadGoogle();
    </script>
</head>

<Layout>
    <div style="padding-left:50px">
        <h1 style="margin-left: 15px">House Points</h1>
    </div>
    <!-- <div style="padding-left:100px">
        <p id="houseId">Your House: Loading...</p>
        <p id="pointsId">Your Points: Loading...</p>
    </div> -->
    {#if window.innerWidth > 769}
        <div style="height: 80vh">
            <div id="chart_div"/>
        </div>
    {:else}
        <div style="height: 70vh">
            <div id="chart_div"/>
        </div>
    {/if}
    <div style="display: flex; flex-direction: row; padding-left: 75px">
        <button id="line_button">History View</button>
        <button id="bar_button">Current Scores</button>
    </div>
</Layout>

<style>
    #chart_div {
        width: 100%;
        height: 100%;
        z-index: 0;
    }
    button {
        margin: 0px 10px;
    }
</style>