<!-- Retrieve ride assignment and match with current user. -->
<!-- If driver, need to display all passengers. If passenger, just display driver. -->
<script>
    export let event;

    async function getUserRides(event) {
        const rides = event.rides;
        const user = await (await fetch(`/api/profile/`)).json();

        let userPool;
        // Return entire carpool user is in
        for (const key in rides) {
            if (rides[key]["driver"]) {
                if (rides[key]["driver"] == user.email) {
                    userPool = rides[key];
                    break;
                }
            }
            for (const email of rides[key]["passengers"]) {
                if (email == user.email) {
                    userPool = rides[key];
                    break;
                }
            }
        }
        return userPool;
    }
</script>

{#if event != null}
    {#await getUserRides(event)}
        <p>Loading...</p>
    {:then userRides}
        {#if userRides != null}
            <h2>Ride Assignment</h2>
            <table>
                <tr>
                    <th>Driver</th>
                </tr>
                <tr>
                    {#if userRides["driver"]}
                        <td>{userRides["driver"]}</td>
                    {:else}
                        <td>None</td>
                    {/if}
                </tr>
                <tr>
                    <th>Passengers</th>
                </tr>
                {#if userRides["passengers"].length != 0}
                    {#each userRides["passengers"] as passenger}
                        <tr>
                            <td>{passenger}</td>
                        </tr>
                    {/each}
                {:else}
                    <tr>
                        <td>None</td>
                    </tr>
                {/if}
            </table>
        {/if}
    {/await}
{/if}

<style>
    table, th, td{
        border: none;
        border-collapse: collapse;
        width: 20%;
    }

    td{
        padding: 10px 15px;
    }

    th {
        padding: 10px;
        background-color: var(--fc-button-bg-color);
        color: white;
    }
</style>