<script>
    import Layout from "../Layout.svelte";
    import { onMount } from 'svelte';
    import {adminStatus} from '../stores.js';
    import Pagination from "../Components/Pagination.svelte";
    import SearchBar from "../Components/SearchBar.svelte";

    let outreachData;
    let filteredData;
    let searchText = "";

    async function getOutreach() {
        let response = await fetch(`/api/outreach/`);
        if (response.status === 200) {
            let users = await response.json();
            users = users.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
            return users;
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getAdminStatus() {
        let response = await fetch(`/api/permissions/`);
        if (response.status === 200) {
            let output = await response.json();
            return output.is_admin;
        } else {
            throw new Error(response.statusText);
        }
    }

    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'hours', "title": "Hours"},
        {"value": 'car', "title": 'Car'},
        {"value": 'outreach_course', "title": "Class"},
        {"value": 'quarter', "title": "Quarter"}
    ]



    let classes = [
        'CSE',
        'ECE',
        'MAE'
    ]

    let cars = [
        'Yes',
        'No'
    ]
    let quarters = []


    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;
        } else {
            ascending = true;
        }
        sorting_col = header["value"];

        if (ascending) {
            outreachData = outreachData.sort((first, second) => {
                if (first[sorting_col] < second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            outreachData = outreachData.sort((first, second) => {
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

    let class_option;
    let car_option;
    let quarter_option;

    let csv_data;
    let outreachDataPerPage;

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
                if (j == 0 && i != 0) {
                    var element = cols[j].querySelector('a');
                    csvrow.push(element.innerHTML);
                } else {
                    csvrow.push(cols[j].innerHTML);
                }
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
        hiddenElement.download = 'outreach_students.csv';
        hiddenElement.click();
    }
    function filter() {
        filteredData = outreachData.filter((outreachStudent) => {
            return (class_option == "all" || outreachStudent.outreach_course == class_option)
                && (car_option == "all" || outreachStudent.car == car_option)
                && (quarter_option == "all" || outreachStudent.quarter == quarter_option)
                && ((outreachStudent.preferred_name.toLowerCase() + " " + outreachStudent.last_name.toLowerCase()).includes(searchText.toLowerCase())
                    || outreachStudent.email.toLowerCase().includes(searchText.toLowerCase()));
        })

    }
    onMount(async () => {
        outreachData = await getOutreach();

        quarters = outreachData.map((outreachStudent) => {
            return outreachStudent.quarter;
        })
        quarters = [...new Set(quarters)];


    })
    $: {
        car_option, class_option, searchText, quarter_option;
        if (outreachData) filter();
        }
</script>
<svelte:head>
    <title> HKN Portal | Outreach Students </title>
</svelte:head>
<Layout>
    <main>
        {#if $adminStatus === true}
            <div style="padding-left:50px">
                <h1 style="margin-left: 15px">Outreach Students</h1>
                {#if filteredData}
                    <section class="top_bar">
                        <div>
                            <form>
                                <select bind:value={class_option} name="classes">
                                    <option value="all">Filter by Class</option>
                                    {#each classes as curr_class}
                                        <option value={curr_class}>{curr_class}</option>
                                    {/each}
                                </select>
                            </form>
                        </div>
                        <div>
                            <form>
                                <select bind:value={car_option} name="cars">
                                    <option value="all">Filter by Car</option>
                                    {#each cars as car}
                                        <option value={car}>{car}</option>
                                    {/each}
                                </select>
                            </form>
                        </div>

                        <div>
                            <form>
                                <select bind:value={quarter_option} name="quarters">
                                    <option value="all">Filter by Quarter</option>
                                    {#each quarters as quarter}
                                        <option value={quarter}>{quarter}</option>
                                    {/each}
                                </select>
                            </form>
                        </div>



                        <SearchBar bind:searchText />
                        <div>
                            <button id="downloadButton" type="button" on:click={() => download_table()}>
                                Download as CSV
                            </button>
                        </div>
                    </section>
                    {#if outreachDataPerPage}
                        <table>
                            <tr>
                                {#each headers as header}
                                    {#if (sorting_col != header['value'])}
                                        <th on:click={() => sortBy(header)}>{header["title"]}</th>
                                    {:else if (ascending)}
                                        <th on:click={() => sortBy(header)}>{header["title"]}⏶</th>
                                    {:else}
                                        <th on:click={() => sortBy(header)}>{header["title"]}⏷</th>
                                    {/if}
                                {/each}
                            </tr>

                        {#each outreachDataPerPage as outreachStudent}
                            {#if (class_option == "all" || outreachStudent.outreach_course == class_option)
                                && (car_option == "all" || outreachStudent.car == car_option)}
                                <tr>
                                    <td>
                                        {#if adminStatus}
                                            <a href="/profile/{outreachStudent.user_id}">{outreachStudent.preferred_name}</a>
                                        {:else}
                                            {outreachStudent.preferred_name}
                                        {/if}
                                    </td>
                                    <td>
                                        {outreachStudent.last_name}
                                    </td>
                                    <td>
                                        {outreachStudent.email}
                                    </td>
                                    <td style="text-align: center">
                                        {outreachStudent.hours}
                                    </td>
                                    <td style="text-align: center">
                                        {outreachStudent.car}
                                    </td>
                                    <td style="text-align: center">
                                        {outreachStudent.outreach_course}
                                    </td>
                                    <td style="text-align: center">
                                        {outreachStudent.quarter}
                                </tr>
                            {/if}
                        {/each}
                        </table>

                    {/if}
                    <Pagination rows={filteredData} perPage={15} bind:trimmedRows={outreachDataPerPage} />
                {:else}
                    <h1 style="margin-left: 15px">Loading...</h1>
                {/if}

            </div>
        {:else if $adminStatus === null}
            <div>
                <h1 style="margin-left: 15px">Loading...</h1>
            </div>
        {:else}
            <div>
                <h1 style="margin-left: 15px">You aren't supposed to be here >:(</h1>
            </div>
        {/if}
    </main>
</Layout>


<style>
    div {
        float:left;
        padding: 10px;
    }
    .top_bar {
        display: flex;
        justify-content: start;
        align-items: start;
        flex-wrap: wrap;
    }
    table {
        /* border: 1px solid grey; */
        border-radius:20px;
        border:solid gray 1px;
        border-collapse: separate;
        height: 60%;
        width: 100%;
        overflow:hidden;
        border-spacing:0;
        float:left;
    }
    th {
        border-collapse: collapse;
        padding-top: 10px;
        padding-bottom: 10px;
        background-color: rgb(44,62,80);
        color: white;
        text-transform: capitalize;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    th:hover {
        cursor: pointer;
        background-color: rgb(24,42,60);
    }
    th:nth-child(1) {
        width: 15%;
    }
    th:nth-child(2) {
        width: 15%;
    }
    th:nth-child(3) {
        width: 25%;
    }
    th:nth-child(4) {
        width: 10%;
    }
    th:nth-child(5) {
        width: 10%;
    }
    th:nth-child(6) {
        width: 10%;
    }
    tr:nth-child(odd) {
        background-color: rgb(240,240,255);
    }
    td {
        padding: 10px;
        overflow: wrap;
    }

    #downloadButton:hover {
        cursor: pointer;
    }

</style>