<script>
    import { onMount } from "svelte";
 
    async function getOutreach() {
        let response = await fetch(`/api/outreach/`);
        if (response.status === 200) {
            let users = await response.json();
            return users
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
</script>

<svelte:head>
    <title> HKN Portal | Outreach Students </title>
</svelte:head>

{#await Promise.all([getOutreach(), getAdminStatus()])}
    <div>
        <p>loading...</p>
    </div>
{:then [outreachData, adminStatus]}

<main>
    {#if adminStatus}
        <div>
            <h1 style="margin-left: 15px">Outreach Students</h1>
            <table>
                <tr>
                    <th>User</th>
                    <th>Email</th>
                    <th>Hours</th>
                    <th>Car?</th>
                    <th>Class</th>
                </tr>
            {#each outreachData as outreachStudent}
                <tr>
                    <td>
                        {outreachStudent.preferred_name} {outreachStudent.last_name}
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