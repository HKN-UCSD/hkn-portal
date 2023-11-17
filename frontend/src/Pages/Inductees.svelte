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

let years = [
    2023, 2024, 2025, 2026, 2027
]

    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'major', "title": 'Major'},
        {"value": 'grad_year', "title": 'Year'},
        {"value": 'professional_points', "title": 'Pro'},
        {"value": 'social_points', "title": 'Social'},
        {"value": 'technical_points', "title": 'Tech'},
        {"value": 'outreach_points', "title": 'Outreach'},
        {"value": 'mentorship_points', "title": 'Mentor'},
        {"value": 'general_points', "title": 'General'},
        {"value": 'total_points', "title": 'Total Points'}
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

</script>

<svelte:head>
    <title> HKN Portal | Inductees </title>
</svelte:head>

{#await Promise.all([getInductees(), getAdminStatus()])}
    <div>
        <h1 style="margin-left: 15px">Inductees</h1>
        <p>loading...</p>
    </div>
{:then [filler, adminStatus]}

<main>
    {#if adminStatus}
        <div>
            <h1 style="margin-left: 15px">Inductees</h1>
            <form>
                <label for="majors">Filter by major:</label>
                <select bind:value={major_option} name="majors">
                    <option value="all">All Majors</option>
                    {#each majors as major}
                        <option value={major}>{major}</option>
                    {/each}
                </select>
            </form>
            <form>
                <label for="years">Filter by Year:</label>
                <select bind:value={year_option} name="years">
                    <option value="all">Any</option>
                    {#each years as year}
                        <option value={year}>{year}</option>
                    {/each}
                    <option value="after">> 2026</option>
                </select>
            </form>
            <table>
                <tr>
                    {#each headers as header}
                        <th on:click={() => sortBy(header)}>{header["title"]}</th>
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
                        <td>
                            {inducteeData.grad_year}
                        </td>
                        <td>
                            {inducteeData.professional_points}
                        </td>
                        <td>
                            {inducteeData.social_points}
                        </td>
                        <td>
                            {inducteeData.technical_points}
                        </td>
                        <td>
                            {inducteeData.outreach_points}
                        </td>
                        <td>
                            {inducteeData.mentorship_points}
                        </td>
                        <td>
                            {inducteeData.general_points}
                        </td>
                        <td>
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