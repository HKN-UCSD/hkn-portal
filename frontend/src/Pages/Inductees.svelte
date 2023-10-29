<script>
    import { onMount } from "svelte";
 
    async function getInductees() {
        let response = await fetch(`/api/inductees/`);
        if (response.status === 200) {
            let users = await response.json();
            return users
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getAdminStatus() {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let otherActions = availableActions.other_actions;
            return otherActions;
        } else {
            throw new Error(response.statusText);
        }
    }
</script>

<svelte:head>
    <title> HKN Portal | Inductees </title>
</svelte:head>

{#await Promise.all([getInductees(), getAdminStatus()])}
    <div>
        <p>loading...</p>
    </div>
{:then [inducteesData, otherActions]}




<main>
    {#if otherActions.length > 0}
        <div>
            <h1 style="margin-left: 15px">Inductees</h1>
            <table>
                <tr>
                    <th>User</th>
                    <th>Email</th>
                    <th>Major</th>
                    <th>Grad Year</th>
                    <th>Professional Points</th>
                    <th>Social Points</th>
                    <th>Technical Points</th>
                    <th>Outreach Points</th>
                    <th>Mentorship Points</th>
                    <th>General Points</th>
                    <th>Total</th>
                </tr>
            {#each inducteesData as inducteeData}
                <tr>
                    <td>
                        {inducteeData.preferred_name} {inducteeData.last_name}
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