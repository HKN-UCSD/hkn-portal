<!-- Retrieve ride assignment and match with current user. -->
<!-- If driver, need to display all passengers. If passenger, just display driver. -->
<script>
    export let event;

    // Determine if the current user has RSVP'd for the event
    // Parameters: none
    // Output: true if user has RSVP'd, false otherwise
    async function RSVPd() {
        const user = await (await fetch(`/api/profile/self/`)).json();
        const actionRecords = await (await fetch(`/api/eventactionrecords/`)).json();
        const eventRSVPs = actionRecords.filter(record => record.event == event.pk && record.action == "RSVP");

        if (eventRSVPs.find(record => record.acted_on == user.user_id)) {
            return true;
        }

        return false;
    }

    // Gets the carpool that the current user is in
    // Parameters: none
    // Output: a JSON object representing the carpool the user is in
    //         format of JSON object: {"driver": attendee, "passengers": [list of attendees]}
    async function getUserRides() {
        // Check if user is RSVP'd
        const RSVP = await RSVPd();
        if (!RSVP) {
            return null;
        }

        // Define function to parse email from "First Last (Email)"
        function parseEmail(attendee) {
            return attendee.split("(")[1].split(")")[0];
        }

        const rides = event.rides;
        const user = await (await fetch(`/api/profile/self/`)).json();

        let userPool = null;

        // Set userPool to the carpool that the current user is in
        for (const key in rides) {
            if (rides[key]["driver"]) {
                const driverEmail = parseEmail(rides[key]["driver"]);
                if (driverEmail == user.email) {
                    return rides[key];
                }
            }
            for (const passenger of rides[key]["passengers"]) {
                const passengerEmail = parseEmail(passenger);
                if (passengerEmail == user.email) {
                    return rides[key]
                }
            }
        }

        // null if user is not in any carpool
        return userPool;
    }
</script>

{#if event != null}
    {#await getUserRides()}
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
        max-width: 40%;
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