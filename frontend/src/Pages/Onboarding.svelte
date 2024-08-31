
<script>
    import { onMount } from 'svelte';
    import Layout from '../Layout.svelte';
    import {adminStatus} from '../stores.js';
    import SearchBar from "../Components/SearchBar.svelte";
    import Pagination from "../Components/Pagination.svelte";


    let onboardingOfficers = [];

    /* Status fields */
    let loading = true;
    let error = null;

    /* Fields used in the top bar(Sort, Filter, Search, Download) */
    // Sort
    let ascending = true;
    let sorting_col = "N/A";

    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;

        } else {
            ascending = true;
        }
        sorting_col = header["value"];

        if (ascending) {
            onboardingOfficers = onboardingOfficers.sort((first, second) => {
                if (first[sorting_col] < second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            console.log("REVERSO");
            onboardingOfficers = onboardingOfficers.sort((first, second) => {
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

    // Filter
    let filteredData;
    let quarter_option;
    let quarters = [];


    // Search
    let searchText = "";

    // Download
    let csv_data;

    // Paging
    let onboardingDataPerPage = [];
    

    let headers = [
        {"value": 'first_name', "title": "First Name"},
        {"value": 'last_name', "title": "Last Name"},
        {"value": 'position', "title": "Position"},
        {"value": "quarter_name", "title": "Quarter Inducted"},
        {"value": "new_officer", "title": "New Officer"}
                  ]



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////



    /*
    * Gets Officers as well as the objects additional data via the foreign key
    */
    async function getOfficer() {
        try {
            let response = await fetch(`/api/officers/`);
            if (response.ok) {
                let onboardings = await response.json();
                return onboardings
            } else {
                throw new Error(response.statusText);
            }
        } catch (err) {
            error = err.message;
        } finally {
            loading = false;
        }
    }


    /* Existing Helper Functions */

    /*
    * Gets the status/priviledge of the user
    */
    async function getAdminStatus() {
        let response = await fetch(`/api/permissions/`);
        if (response.status === 200) {
            let output = await response.json();
            return output.is_admin;
        } else {
            throw new Error(response.statusText);
        }
    }

    /*
    * Filters out the table based on the information provided in the fields
    */

    function filter() {
        filteredData = onboardingOfficers.filter(onboarding => {
            return (quarter_option == "all" || onboarding.quarter_name == quarter_option)
                    && (searchText == "" || (onboarding.preferred_name.toLowerCase() 
                    + " " + onboarding.last_name.toLowerCase()).includes(searchText.toLowerCase())
                        || onboarding.position.toLowerCase().includes(searchText.toLowerCase()));
        });
    }

    /*
    * Converts existing table to CSV data 
    */
    function tableToCSV() {
        let csv = [];
        let row = [];
        // Add the headers to the CSV
        headers.forEach(header => {
            row.push(header['title']);
        });
        csv.push(row.join(','));
        // Add the data to the CSV
        onboardingOfficers.forEach(onboardingOfficers => {
            row = [];
            row.push(onboardingOfficers.first_name);
            row.push(onboardingOfficers.last_name);
            row.push(onboardingOfficers.position);
            row.push(onboardingOfficers.quarter_name);
            row.push(onboardingOfficers.new_officer);
            csv.push(row.join(','));
        });
        csv_data = csv;
        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

    }

    /*
    * Downloads the table client side through calling tableToCSV()
    * to convert relevant data
    */
    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'onboarding.csv';
        hiddenElement.click();
    }

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Fetch data when the component is mounted
    onMount(async () => {
        onboardingOfficers = await getOfficer();
        // Extract unique values for quarter_name
        const uniqueQuarterNames = new Set(onboardingOfficers.map(item => item.quarter_name));

        // Convert sets to arrays for easier use or display
        quarters = Array.from(uniqueQuarterNames);

    });

    $: {
        quarter_option, searchText;
        if (onboardingOfficers) filter();
        }
</script>



<!-------------------------------------------------------------------------------------------------------------->



<svelte:head>
    <title> HKN Portal | Onboarding Officers </title>
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
                        <select bind:value={quarter_option} name="quarter">
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
                    <table id="onboardingTable">
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
                    {#if onboardingDataPerPage}
                        {#each onboardingDataPerPage as onboarding}
                        <tr>
                            <td>
                                <a href="/profile/{onboarding.user_id}">{onboarding.preferred_name}</a>
                            </td>
                            <td>
                                {onboarding.last_name}
                            </td>
                            <td>
                                {onboarding.position}
                            </td>
                            <td>
                                {onboarding.quarter_name}
                            </td>
                            <td>
                                {onboarding.new_officer ? 'Yes' : 'No'}
                            </td>
                        </tr>
                        {/each}
                    {/if}
                    </table>
                {/if}
            <section class="bottom_bar">
                <Pagination rows={filteredData} perPage={15} bind:trimmedRows={onboardingDataPerPage} />
            </section>
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

<!-------------------------------------------------------------------------------------------------------------->


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