<script>
    import { onMount } from "svelte";

    let outreachData;
 
    async function getOutreach() {
        let response = await fetch(`/api/outreach/`);
        if (response.status === 200) {
            let users = await response.json();
            outreachData = users;
            outreachData = outreachData.sort((first, second) => {
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
        {"value": 'car', "title": 'Car?'},
        {"value": 'outreach_course', "title": "Class"}
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

</script>

<svelte:head>
    <title> HKN Portal | Outreach Students </title>
</svelte:head>

{#await Promise.all([getOutreach(), getAdminStatus()])}
    <div>
        <p>loading...</p>
    </div>
{:then [filler, adminStatus]}

<main>
    {#if adminStatus}
        <div>
            <h1 style="margin-left: 15px">Outreach Students</h1>
            <form>
                <label for="classes">Filter by Class:</label>
                <select bind:value={class_option} name="classes">
                    <option value="all">All Classes</option>
                    {#each classes as curr_class}
                        <option value={curr_class}>{curr_class}</option>
                    {/each}
                </select>
            </form>
            <form>
                <label for="cars">Filter by Car:</label>
                <select bind:value={car_option} name="cars">
                    <option value="all">Any</option>
                    {#each cars as car}
                        <option value={car}>{car}</option>
                    {/each}
                </select>
            </form>
            <table>
                <tr>
                    {#each headers as header}
                        <th on:click={() => sortBy(header)}>{header["title"]}</th>
                    {/each}
                </tr>
            {#each outreachData as outreachStudent}
                {#if (class_option == "all" || outreachStudent.outreach_course == class_option)
                    && (car_option == "all" || outreachStudent.car == car_option)}
                    <tr>
                        <td>
                            {outreachStudent.preferred_name}
                        </td>
                        <td>
                            {outreachStudent.last_name}
                        </td>
                        <td>
                            {outreachStudent.email}
                        </td>
                        <td>
                            {outreachStudent.hours}
                        </td>
                        <td>
                            {outreachStudent.car}
                        </td>
                        <td>
                            {outreachStudent.outreach_course}
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
        padding: 30px;
        padding-top: 10px;
        margin: 30px;
    }
    table, th, td{
        /* border: 1px solid grey; */
        border: none;
        border-collapse: collapse;
    }

    td{
        padding: 10px 15px;
    }

    th {
        padding: 15px;
        /* border-spacing: 5px; */
    }

    th {
        background-color: var(--fc-button-bg-color);
        color: white;
    }
</style>