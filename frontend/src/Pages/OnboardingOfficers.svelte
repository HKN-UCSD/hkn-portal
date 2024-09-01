<script>
    import { onMount } from "svelte";
    import Layout from "../Layout.svelte";
    import Pagination from "../Components/Pagination.svelte";
    import SearchBar from "../Components/SearchBar.svelte";
    import { adminStatus } from '../stores.js';


    let positions = [];
    let quarters = [];

    // OrderedDict([('user_id', '4678f6e9-81ab-4d0c-bab9-91a73cd51fd7'), 
    // ('email', 'mzamorano@ucsd.edu'), 
    // ('first_name', 'Max'), 
    // ('preferred_name', 'Max'), 
    // ('middle_name', None), 
    // ('last_name', 'Zamorano'), 
    // ('induction_class', None), 
    // ('pronouns', None), 
    // ('position', 'MAE Outreach Chair'), 
    // ('onboarding', 'Previous'), 
    // ('quarter', 'Previous'), 
    // ('new_officer', False)])]

    let users = []

    async function getOfficer() {
        let response = await fetch(`/api/officers/`);
        if (response.status === 200) {
            users = await response.json();
            users = users.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
            for (let i = 0; i < users.length; i++) {
                if (!positions.includes(users[i].position)) {
                    positions.push(users[i].position);
                    }
                if (!quarters.includes(users[i].quarter)) {
                    quarters.push(users[i].quarter);
                    }
            }
            positions.sort();
            quarters.sort();
            return users;
        } else {
            throw new Error(response.statusText);
        }
    }
    
    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'position', "title": 'Position'},
        {"value": 'quarter', "title": 'Quarter Inducted'},
        {"value": 'new_officer', "title": 'New Officer'}
    ]

    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;

        } else {
            ascending = true;
        }
        sorting_col = header["value"];

        if (ascending) {
            officersData = officersData.sort((first, second) => {
                if (first[sorting_col] < second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            officersData = officersData.sort((first, second) => {
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

    let position_option;
    let quarter_option;
    let searchText = "";
    
    let csv_data;

    function tableToCSV() {
        let csv = [];
        let row = [];
        // Add the headers to the CSV
        headers.forEach(header => {
            row.push(header['title']);
        });
        csv.push(row.join(','));
        // Add the data to the CSV
        officersData.forEach(officerData => {
            row = [];
            row.push(officerData.preferred_name);
            row.push(officerData.last_name);
            row.push(officerData.position);
            row.push(officerData.quarter);
            row.push(officerData.new_officer);
            csv.push(row.join(','));
        });
        csv_data = csv;
        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

    }

    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'officers.csv';
        hiddenElement.click();
    }
    let filteredData = [];

    function filter() {
        filteredData = officersData.filter(officerData => {
            return (position_option == "all" || officerData.position == position_option)
                    && (quarter_option == "all" || officerData.quarter == quarter_option)
                    && (searchText == "" || (officerData.preferred_name.toLowerCase() + " " + 
                    officerData.last_name.toLowerCase()).includes(searchText.toLowerCase())
                    );
        });
    }

    let officersData = [];

    let officerDataPerPage = [];

    onMount(async () => {
        officersData = await getOfficer();
        console.log(position_option)
    });
    $: {
        position_option, quarter_option, searchText;
        if (officersData) filter();
    }
 </script>
 
 <svelte:head>
     <title> HKN Portal | Onboarding Officers </title>
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
 </svelte:head>
 
 <Layout>
    <main>
        {#if $adminStatus === true}
            <div style="padding-left:50px">
                <h1 style="margin-left: 15px">Onboarding Officers</h1>  
                {#if filteredData}
                    <section class="top_bar">
                        <div>
                            <form>
                                <select bind:value={position_option} name="positions">
                                    <option value="all">Filter by Position</option>
                                    {#each positions as position}
                                        <option value={position}>{position}</option>
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

                        <SearchBar bind:searchText/>

                        <div>
                            <button id="downloadButton" type="button" on:click={() => download_table()}>
                                Download as CSV
                            </button>
                        </div>
                    </section>

                    <table id="officerTable">
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
                        {#if officerDataPerPage}
                            {#each officerDataPerPage as officerData}
                                <tr>
                                    <td>
                                        <a href="/profile/{officerData.user_id}">{officerData.preferred_name}</a>
                                    </td>
                                    <td>
                                        {officerData.last_name}
                                        
                                    </td>
                                    <td>
                                        {officerData.position}
                                    </td>
                                    <td>
                                        {officerData.quarter}
                                    </td>
                                    <td>
                                        {officerData.new_officer}
                                    </td>
                                </tr>
                            {/each}
                        {/if}
                    </table>
                    <section class="bottom_bar">

                        <Pagination rows={filteredData} perPage={15} bind:trimmedRows={officerDataPerPage} />
                    </section>

                {:else}
                    <h1 style="margin-left: 15px">Loading</h1>
                {/if}
            </div>
        {:else if $adminStatus == null}
            <div>
                <h1 style="margin-left: 15px"> Loading...</h1>
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