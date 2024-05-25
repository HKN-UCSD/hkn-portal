<script>
    import Navbar from "../Components/Navbar.svelte";
    import Layout from "../Layout.svelte";
    import Pagination from "../Components/Pagination.svelte";
    import { onMount } from "svelte";
    import { adminStatus } from '../stores.js';
    import SearchBar from "../Components/SearchBar.svelte";


    async function getMajors() {
        return await (await(fetch(`api/majors/`))).json()
    }

    let majors = [];
    let years = [];

    async function getInductees() {
        let response = await fetch(`/api/inductees/`);
        if (response.status === 200) {
            let possible_majors = (await getMajors()).map(major => major.name)
            let users = await response.json();
            users.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
            for (let i = 0; i < users.length; i++) {
                if (!majors.includes(users[i].major) && possible_majors.includes(users[i].major)) {
                    majors.push(users[i].major);
                }
                if (!years.includes(users[i].grad_year)) {
                    years.push(users[i].grad_year);
                }
            }
            majors.sort();
            years.sort();
            majors.push('Other');
            return users;
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getInductionClasses() {
        let response = await fetch(`/api/inductionclasses/`);
        if (response.status === 200) {
            let output = await response.json();
            return output;
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

    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'major', "title": 'Major'},
        {"value": 'grad_year', "title": 'Year'},
        {"value": 'induction_class', "title": 'Class'},
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
    let class_option;
    let searchText = "";

    let csv_data;

    /*
    * Convert the inducteesData data to CSV format

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
        inducteesData.forEach(inducteeData => {
            row = [];
            row.push(inducteeData.preferred_name);
            row.push(inducteeData.last_name);
            row.push(inducteeData.email);
            row.push(inducteeData.major);
            row.push(inducteeData.grad_year);
            row.push(inducteeData.induction_class);
            row.push(inducteeData.professional_points);
            row.push(inducteeData.social_points);
            row.push(inducteeData.technical_points);
            row.push(inducteeData.outreach_points);
            row.push(inducteeData.mentorship_points);
            row.push(inducteeData.general_points);
            row.push(inducteeData.total_points);
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
        hiddenElement.download = 'inductees.csv';
        hiddenElement.click();
    }
    let filteredData;

    function filter() {
        filteredData = inducteesData.filter(inducteeData => {
            return (major_option == "all" || inducteeData.major == major_option
                        || (major_option == "Other" && !majors.includes(inducteeData.major)))
                    && (year_option == "all" || inducteeData.grad_year == parseInt(year_option))
                    && (class_option == "all" || inducteeData.induction_class == class_option)
                    && (searchText == "" || (inducteeData.preferred_name.toLowerCase() + " " + inducteeData.last_name.toLowerCase()).includes(searchText.toLowerCase())
                        || inducteeData.email.toLowerCase().includes(searchText.toLowerCase()));
        });
    }

    let inducteesData, classes;

    let inducteeDataPerPage;

    onMount(async () => {
        inducteesData = await getInductees();
        classes = await getInductionClasses();
        console.log(inducteesData)
    });
    // filter the data when the inducteesData and classes are loaded if any of the options changes
    $: {
        major_option, year_option, class_option, searchText;
        if (inducteesData && classes) filter();
        }
</script>

<svelte:head>
    <title> HKN Portal | Inductees </title>
</svelte:head>



<Layout>

    {#if $adminStatus === true}
        <div style="padding-left:50px">
            <h1 style="margin-left: 15px">Inductees</h1>
            {#if filteredData}
                <section class="top_bar">
                    <div >
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
                            </select>
                        </form>
                    </div>
                    {#if classes}
                        <div>
                            <form>
                                <select bind:value={class_option} name="classes">
                                    <option value="all">Filter by Induction Class</option>
                                    {#each classes as inductionClass}
                                        <option value={inductionClass.name}>{inductionClass.name}</option>
                                    {/each}
                                </select>
                            </form>
                        </div>
                    {/if}

                    <SearchBar bind:searchText/>

                    <div>
                        <button id="downloadButton" type="button" on:click={() => download_table()}>
                            Download as CSV
                        </button>
                    </div>
                </section>

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
                        {/each}
                    </tr>
                    {#if inducteeDataPerPage}
                        {#each inducteeDataPerPage as inducteeData}
                                <tr>
                                    <td>
                                        <a href="/profile/{inducteeData.user_id}">{inducteeData.preferred_name}</a>
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
                                        {inducteeData.induction_class}
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

                        {/each}
                    {/if}
                </table>
                <section class="bottom_bar">

                    <Pagination rows={filteredData} perPage={15} bind:trimmedRows={inducteeDataPerPage} />
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

    #downloadButton:hover {
        cursor: pointer;
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