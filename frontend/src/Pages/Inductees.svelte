<script>
    import { onMount } from "svelte";

    let inducteesData;
 
    async function getInductees() {
        let response = await fetch(`/api/inductees/`);
        if (response.status === 200) {
            let users = await response.json();
            inducteesData = users;
            inducteesData = inducteesData.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
            inducteesData = users;
            inducteesData = inducteesData.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getAdminStatus() {
        let response = await fetch(`/api/permissions/`);
        if (response.status === 200) {
            let output = await response.json();
            let admin = output.is_admin;
            return admin;
        } else {
            throw new Error(response.statusText);
        }
    }

let majors = [
    'BENG: Bioengineering',
    'BENG: Bioinformatics',
    'BENG: Biotechnology',
    'BENG: BioSystems',
    'CSE: Computer Engineering',
    'CSE: Computer Science',
    'CSE: CS_Bioinformatics',
    'DSC: Data Science',
    'ECE: Computer Engineering',
    'ECE: Electrical Engineering',
    'ECE: EE and Society',
    'ECE: Engineering Physics',
    'MAE: Aerospace Engineering',
    'MAE: Environmental Engineering',
    'MAE: Mechanical Engineering',
    'MATH: Math-CS',
    'Other'
]
let majors = [
    'BENG: Bioengineering',
    'BENG: Bioinformatics',
    'BENG: Biotechnology',
    'BENG: BioSystems',
    'CSE: Computer Engineering',
    'CSE: Computer Science',
    'CSE: CS_Bioinformatics',
    'DSC: Data Science',
    'ECE: Computer Engineering',
    'ECE: Electrical Engineering',
    'ECE: EE and Society',
    'ECE: Engineering Physics',
    'MAE: Aerospace Engineering',
    'MAE: Environmental Engineering',
    'MAE: Mechanical Engineering',
    'MATH: Math-CS',
    'Other'
]

let years = [
    2023, 2024, 2025, 2026, 2027
]

    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'major', "title": 'Major'},
        {"value": 'grad_year', "title": 'Year'},
        {"value": 'professional_points', "title": 'P'},
        {"value": 'social_points', "title": 'S'},
        {"value": 'technical_points', "title": 'T'},
        {"value": 'outreach_points', "title": 'O'},
        {"value": 'mentorship_points', "title": 'M'},
        {"value": 'general_points', "title": 'G'},
        {"value": 'total_points', "title": 'Total'}
        {"value": 'professional_points', "title": 'P'},
        {"value": 'social_points', "title": 'S'},
        {"value": 'technical_points', "title": 'T'},
        {"value": 'outreach_points', "title": 'O'},
        {"value": 'mentorship_points', "title": 'M'},
        {"value": 'general_points', "title": 'G'},
        {"value": 'total_points', "title": 'Total'}
    ]

    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;

        } else {
            ascending = true;
        }
        sorting_col = header["value"];

        if (ascending) {
            inducteesData = inducteesData.sort((first, second) => {
                if (first[sorting_col] < second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            inducteesData = inducteesData.sort((first, second) => {
                if (first[sorting_col] > second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        }
    }
    

    let sorting_col = "N/A";
    let ascending = true;

    let major_option;
    let year_option;

    let csv_data;
    
    function tableToCSV() {

        // Variable to store the final csv data
        csv_data = [];

        // Get each row data
        var rows = document.getElementsByTagName('tr');
        for (var i = 0; i < rows.length; i++) {

            // Get each column data
            var cols = rows[i].querySelectorAll('td,th');

            // Stores each csv row data
            var csvrow = [];
            for (var j = 0; j < cols.length; j++) {

                // Get the text data of each cell
                // of a row and push it to csvrow
                csvrow.push(cols[j].innerHTML);
            }

            // Combine each column value with comma
            csv_data.push(csvrow.join(","));
        }

        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

    }


    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'inductees.csv';
        hiddenElement.click();
    }

    let csv_data;
    
    function tableToCSV() {

        // Variable to store the final csv data
        csv_data = [];

        // Get each row data
        var rows = document.getElementsByTagName('tr');
        for (var i = 0; i < rows.length; i++) {

            // Get each column data
            var cols = rows[i].querySelectorAll('td,th');

            // Stores each csv row data
            var csvrow = [];
            for (var j = 0; j < cols.length; j++) {

                // Get the text data of each cell
                // of a row and push it to csvrow
                csvrow.push(cols[j].innerHTML);
            }

            // Combine each column value with comma
            csv_data.push(csvrow.join(","));
        }

        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

    }


    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'inductees.csv';
        hiddenElement.click();
    }

</script>

<svelte:head>
    <title> HKN Portal | Inductees </title>
</svelte:head>

{#await Promise.all([getInductees(), getAdminStatus()])}
    <div style="padding-left:50px">
        <h1 style="margin-left: 15px">Inductees</h1>
        <p>loading...</p>
    </div>
{:then [filler, adminStatus]}

<main>
    {#if adminStatus}
        <div style="padding-left:50px">
        <div style="padding-left:50px">
            <h1 style="margin-left: 15px">Inductees</h1>
            <div>
                <form>
                    <select bind:value={major_option} name="majors">
                        <option value="all">Filter by Major</option>
                        {#each majors as major}
                            <option value={major}>{major}</option>
                        {/each}
                    </select>
                </form>
            </div>
            <div>
                <form>
                    <select bind:value={year_option} name="years">
                        <option value="all">Filter by Year</option>
                        {#each years as year}
                            <option value={year}>{year}</option>
                        {/each}
                        <option value="after">> 2027</option>
                    </select>
                </form>
            </div>
            <div>
                <button type="button" on:click={() => download_table()}>
                    Download as CSV
                </button>
            </div>
            
            <div id="key">
                <div style="padding:0px">
                    <h3 id="side">Key</h3>
                </div>
                <div style="padding-bottom:0px">
                    <h3>Point Categories</h3>
                    <p>P - Professional</p>
                    <p>S - Social</p>
                    <p>T - Technical</p>
                    <p>O - Outreach</p>
                    <p>M - Mentorship</p>
                    <p>G - General (Other)</p>
                </div>
            </div>
            <table id="inducteeTable">
                <tr>
                    {#each headers as header}
                        {#if (sorting_col != header['value'])}
                            <th on:click={() => sortBy(header)}>{header["title"]}</th>
                        {:else if (ascending)}
                            <th on:click={() => sortBy(header)}>{header["title"]}⏶</th>
                        {:else}
                            <th on:click={() => sortBy(header)}>{header["title"]}⏷</th>
                        {/if}
                        {#if (sorting_col != header['value'])}
                            <th on:click={() => sortBy(header)}>{header["title"]}</th>
                        {:else if (ascending)}
                            <th on:click={() => sortBy(header)}>{header["title"]}⏶</th>
                        {:else}
                            <th on:click={() => sortBy(header)}>{header["title"]}⏷</th>
                        {/if}
                    {/each}
                </tr>
                {#each inducteesData as inducteeData}
                    {#if (major_option == "all" || inducteeData.major == major_option)
                        && (year_option == "all" || inducteeData.grad_year == parseInt(year_option) || (inducteeData.grad_year > 2027 && year_option == "after"))}
                        <tr>
                            <td>
                                {inducteeData.preferred_name}
                            </td>
                            <td>
                                {inducteeData.last_name}
                            </td>
                            <td>
                                {inducteeData.email}
                            </td>
                            <td>
                                {inducteeData.major}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.grad_year}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.professional_points}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.social_points}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.technical_points}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.outreach_points}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.mentorship_points}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.general_points}
                            </td>
                            <td style="text-align: center">
                                {inducteeData.total_points}
                            </td>
                        </tr>
                    {/if}
                {/each}
            </table>
        </div>
    {:else}
        <div>
            <h1 style="margin-left: 15px">You aren't supposed to be here >:(</h1>
        </div>
    {/if}
</main>

{/await}

<style>
    div {
        float:left;
        padding: 20px;
        padding-top: 0px;
        float:left;
        padding: 20px;
        padding-top: 0px;
    }
    table {
    table {
        /* border: 1px solid grey; */
        border-radius:20px;
        border:solid gray 1px;
        border-collapse: separate;
        height: 60%;
        overflow:hidden;
        border-spacing:0;
        float:left;
    }
    th {
        border-radius:20px;
        border:solid gray 1px;
        border-collapse: separate;
        height: 60%;
        overflow:hidden;
        border-spacing:0;
        float:left;
    }
    th {
        border-collapse: collapse;
        padding: 10px;
        background-color: rgb(44,62,80);
        color: white;
        text-transform: capitalize;
        width:5%;
    }
    th:hover {
        cursor: pointer;
        background-color: rgb(24,42,60);
    }
    th:nth-child(1) {
        width: 10%;
    }
    th:nth-child(2) {
        width: 10%;
    }
    th:nth-child(3) {
        width: 15%;
        padding: 10px;
        background-color: rgb(44,62,80);
        color: white;
        text-transform: capitalize;
        width:5%;
    }
    th:hover {
        cursor: pointer;
        background-color: rgb(24,42,60);
    }
    th:nth-child(1) {
        width: 10%;
    }
    th:nth-child(2) {
        width: 10%;
    }
    th:nth-child(3) {
        width: 15%;
    }
    th:nth-child(4) {
        width: 15%;
    }
    th:nth-child(5) {
        width: 6%;
    }
    th:nth-child(12) {
        width: 7%;
    }
    tr:nth-child(odd) {
        background-color: rgb(240,240,255);
    }
    td {
        padding: 10px;
        overflow: wrap;
    }
    p, h3 {
        padding:0px;
        margin:0px;
    }
    #key {
        position:fixed;
        top:60px;
        right:-190px;
        font-size:small;
        border: solid black 1px;
        border-radius: 20px;
        background-color: white;
        padding:10px 40px 10px 5px;
        transition: 1s;
        overflow: hidden;
    }
    #key:hover {
        right: -30px;
        transition: 1s;
    }
    #key:hover #side {
        top: -100px;
        transition: 1s;
    }
    #side {
        top: 10px;
        transition: 1s;
        position:relative;
        transform:rotate(-90deg);
    }

</style>